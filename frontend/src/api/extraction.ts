import type { FieldId } from '../fields';

export type ExtractionResult = { field_id: FieldId } & (
  | { status: 'found'; value: string }
  | { status: 'missing'; value: null }
);

const UNREADABLE_RESPONSE = 'The server returned an unreadable response. Please try again.';

function isResult(value: unknown, field: FieldId): value is ExtractionResult {
  if (typeof value !== 'object' || value === null) return false;
  if (!('field_id' in value) || value.field_id !== field) return false;
  if (!('status' in value) || !('value' in value)) return false;
  return (
    (value.status === 'found' && typeof value.value === 'string' && !!value.value.trim()) ||
    (value.status === 'missing' && value.value === null)
  );
}

export async function extractContract(
  file: File,
  selectedFields: readonly FieldId[],
): Promise<ExtractionResult[]> {
  const form = new FormData();
  form.append('file', file);
  selectedFields.forEach((field) => form.append('selected_fields', field));

  let response: Response;
  try {
    response = await fetch('/api/extractions', { method: 'POST', body: form });
  } catch {
    throw new Error('Could not reach the server. Check your connection and try again.');
  }

  const body: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = typeof body === 'object' && body !== null && 'detail' in body
      ? body.detail
      : undefined;
    if (typeof detail === 'string' && detail.trim()) throw new Error(detail);
    if (response.status >= 502 && response.status <= 504) {
      throw new Error('The server is unavailable. Please try again shortly.');
    }
    throw new Error(response.status === 422
      ? 'Check the selected fields and file.'
      : 'Extraction failed. Please try again.');
  }

  if (typeof body !== 'object' || body === null || !('results' in body) ||
      !Array.isArray(body.results) || body.results.length !== selectedFields.length) {
    throw new Error(UNREADABLE_RESPONSE);
  }

  // Reject incomplete or mismatched responses rather than inventing missing values.
  return body.results.map((result: unknown, index) => {
    if (!isResult(result, selectedFields[index])) throw new Error(UNREADABLE_RESPONSE);
    return result;
  });
}
