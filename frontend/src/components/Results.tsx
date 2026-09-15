import type { ExtractionResult } from '../api/extraction';
import { FIELDS, type FieldId } from '../fields';

export interface CompletedExtraction {
  filename: string;
  selectedFields: FieldId[];
  results: ExtractionResult[];
}

export default function Results({ request }: { request: CompletedExtraction }) {
  return (
    <section className="results" aria-labelledby="results-heading">
      <h2 id="results-heading">Extraction results</h2>
      <p className="result-file">{request.filename}</p>
      <p className="hint">
        Results for {request.selectedFields.length} submitted {request.selectedFields.length === 1 ? 'field' : 'fields'}.
      </p>
      <dl className="result-list">
        {request.results.map((result) => (
          <div className="result-row" key={result.field_id}>
            <dt>{FIELDS.find((field) => field.id === result.field_id)!.label}</dt>
            <dd>
              {result.status === 'found' ? result.value : (
                <>
                  <span className="missing-flag">Missing</span>
                  <span className="hint">Not found in this contract.</span>
                </>
              )}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
