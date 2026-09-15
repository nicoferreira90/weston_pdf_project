import { useRef, useState, type FormEvent } from 'react';
import { extractContract } from './api/extraction';
import Results, { type CompletedExtraction } from './components/Results';
import { FIELDS, type FieldId } from './fields';
import './styles.css';

export default function App() {
  const [selectedFields, setSelectedFields] = useState<FieldId[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [completed, setCompleted] = useState<CompletedExtraction | null>(null);
  const [error, setError] = useState('');
  const inFlight = useRef(false);

  const guidance = !selectedFields.length && !file
    ? 'Select at least one field and choose a PDF to continue.'
    : !selectedFields.length
      ? 'Select at least one field to continue.'
      : !file
        ? 'Choose a PDF to continue.'
        : 'Ready to extract your selected fields.';

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (inFlight.current || !file || !selectedFields.length) return;

    const request = { filename: file.name, selectedFields: [...selectedFields] };
    inFlight.current = true;
    setSubmitting(true);
    setCompleted(null);
    setError('');
    try {
      const results = await extractContract(file, request.selectedFields);
      setCompleted({ ...request, results });
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Extraction failed. Please try again.');
    } finally {
      inFlight.current = false;
      setSubmitting(false);
    }
  }

  function toggleField(id: FieldId) {
    setSelectedFields((current) => FIELDS
      .filter((field) => field.id === id ? !current.includes(id) : current.includes(field.id))
      .map((field) => field.id));
  }

  return (
    <main>
      <header>
        <h1>Weston contract extraction</h1>
        <p>Select the details you need, then upload a purchase contract.</p>
      </header>

      <form onSubmit={handleSubmit} aria-busy={submitting}>
        <fieldset disabled={submitting} aria-describedby="fields-help">
          <legend>Fields to extract</legend>
          <p id="fields-help" className="hint">Choose one or more fields.</p>
          <div className="field-options">
            {FIELDS.map((field) => (
              <label className="field-option" key={field.id}>
                <input
                  type="checkbox"
                  checked={selectedFields.includes(field.id)}
                  onChange={() => toggleField(field.id)}
                />
                {field.label}
              </label>
            ))}
          </div>
        </fieldset>

        <div className="upload-section">
          <label htmlFor="contract">Purchase contract</label>
          <p id="file-help" className="hint">Choose one text-based PDF.</p>
          <input
            id="contract"
            type="file"
            accept=".pdf,application/pdf"
            disabled={submitting}
            aria-describedby="file-help selected-file"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <p id="selected-file" className="selected-file">
            {file ? file.name : 'No contract selected.'}
          </p>
        </div>

        <div className="submit-section">
          <button
            type="submit"
            disabled={submitting || !file || !selectedFields.length}
            aria-describedby="submit-help"
          >
            {submitting ? 'Extracting…' : 'Extract fields'}
          </button>
          <p id="submit-help" className="hint">{submitting ? 'Please wait while your contract is processed.' : guidance}</p>
        </div>
      </form>

      <p role="status" className="status-message">
        {submitting ? 'Extracting selected fields.' : completed
          ? `Extraction complete. ${completed.results.filter((result) => result.status === 'found').length} found, ${completed.results.filter((result) => result.status === 'missing').length} missing.`
          : ''}
      </p>
      {error && <div role="alert" className="error-message"><h2>Something went wrong</h2><p>{error}</p></div>}
      {completed && <Results request={completed} />}
    </main>
  );
}
