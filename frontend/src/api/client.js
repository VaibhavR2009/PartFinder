/**
 * src/api/client.js
 *
 * SSE client for PartFinder backend.
 *
 * The backend endpoint POST /api/run streams Server-Sent Events (SSE).
 * Since the native EventSource API only supports GET requests, we use
 * fetch() with a ReadableStream to handle POST + SSE simultaneously.
 *
 * Each SSE event has: { event: string, data: string (JSON) }
 *
 * Known event types from the backend:
 *   - "stage"        : { stage: string, status: "running"|"done" }
 *   - "feasibility"  : { feasible: bool, reason: string, alternative?: string }
 *   - "parts"        : partial or complete parts array
 *   - "result"       : final compiled result object
 *   - "error"        : { message: string }
 *   - "done"         : stream complete signal
 */

/**
 * Parse raw SSE text into { event, data } objects.
 * Handles multi-line data fields and named events.
 *
 * @param {string} text - Raw SSE chunk text
 * @returns {{ event: string, data: string }[]}
 */
function parseSSEChunk(text) {
  const messages = [];
  const blocks = text.split(/\n\n/);

  for (const block of blocks) {
    if (!block.trim()) continue;

    let event = 'message';
    let data = '';

    const lines = block.split('\n');
    for (const line of lines) {
      if (line.startsWith('event:')) {
        event = line.slice(6).trim();
      } else if (line.startsWith('data:')) {
        data += (data ? '\n' : '') + line.slice(5).trim();
      }
      // Ignore 'id:' and 'retry:' for now
    }

    if (data) {
      messages.push({ event, data });
    }
  }

  return messages;
}

/**
 * Run the PartFinder pipeline via POST SSE.
 *
 * @param {Object}   projectData  - Form payload to send as JSON body
 * @param {Function} onEvent      - Called for each SSE event: (eventType, parsedData) => void
 * @param {Function} onDone       - Called when stream finishes cleanly
 * @param {Function} onError      - Called on network/parse errors: (error) => void
 * @returns {Function}            - Abort function to cancel the request
 */
export function runPartFinder(projectData, onEvent, onDone, onError) {
  const controller = new AbortController();

  (async () => {
    try {
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache',
        },
        body: JSON.stringify(projectData),
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Unknown error');
        throw new Error(`Server error ${response.status}: ${errorText}`);
      }

      if (!response.body) {
        throw new Error('Response body is null — streaming not supported');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          // Process any remaining buffer content
          if (buffer.trim()) {
            const messages = parseSSEChunk(buffer + '\n\n');
            for (const { event, data } of messages) {
              _dispatchEvent(event, data, onEvent);
            }
          }
          onDone();
          break;
        }

        buffer += decoder.decode(value, { stream: true });

        // Process all complete SSE blocks (separated by double newlines)
        const parts = buffer.split(/\n\n/);
        // Keep the last (potentially incomplete) block in the buffer
        buffer = parts.pop() ?? '';

        for (const part of parts) {
          if (!part.trim()) continue;
          const messages = parseSSEChunk(part + '\n\n');
          for (const { event, data } of messages) {
            _dispatchEvent(event, data, onEvent);
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') return; // User cancelled — don't call onError
      console.error('[PartFinder SSE] Error:', err);
      onError(err);
    }
  })();

  // Return abort function so callers can cancel
  return () => controller.abort();
}

/**
 * Internal helper: parse JSON data and dispatch to onEvent callback.
 */
function _dispatchEvent(event, data, onEvent) {
  try {
    const parsed = JSON.parse(data);
    onEvent(event, parsed);
  } catch {
    // Non-JSON data — pass as raw string
    onEvent(event, data);
  }
}
