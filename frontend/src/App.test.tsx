import { act, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';

const fetchMock = vi.fn<typeof fetch>();
const contract = new File(['synthetic contract'], 'contract.pdf', { type: 'application/pdf' });
const foundPrice = { field_id: 'purchase_price', status: 'found', value: 'UF 8.500' };
const missingAddress = { field_id: 'property_address', status: 'missing', value: null };

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

async function prepare() {
  const user = userEvent.setup();
  render(<App />);
  await user.click(screen.getByRole('checkbox', { name: 'Purchase price' }));
  await user.upload(screen.getByLabelText('Purchase contract'), contract);
  return user;
}

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal('fetch', fetchMock);
});
afterEach(() => vi.unstubAllGlobals());

describe('extraction workflow', () => {
  it('starts unchecked, requires fields and a file, and supports keyboard selection', async () => {
    const user = userEvent.setup();
    render(<App />);
    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes).toHaveLength(4);
    checkboxes.forEach((checkbox) => expect(checkbox).not.toBeChecked());
    const submit = screen.getByRole('button', { name: 'Extract fields' });
    expect(submit).toBeDisabled();
    await user.tab();
    expect(checkboxes[0]).toHaveFocus();
    await user.keyboard(' ');
    expect(checkboxes[0]).toBeChecked();
    expect(submit).toBeDisabled();
    expect(screen.getByText('Choose a PDF to continue.')).toBeVisible();
    const input = screen.getByLabelText('Purchase contract');
    expect(input).not.toHaveAttribute('multiple');
    await user.upload(input, contract);
    expect(submit).toBeEnabled();
    await user.click(checkboxes[0]);
    expect(submit).toBeDisabled();
    expect(screen.getByText('Select at least one field to continue.')).toBeVisible();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('submits only selected fields, locks controls, and shows found and missing results', async () => {
    let resolve!: (response: Response) => void;
    fetchMock.mockImplementationOnce(() => new Promise((done) => { resolve = done; }));
    const user = await prepare();
    await user.click(screen.getByRole('checkbox', { name: 'Property address' }));
    await user.click(screen.getByRole('button', { name: 'Extract fields' }));

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe('/api/extractions');
    expect(options?.method).toBe('POST');
    expect(options?.headers).toBeUndefined();
    const body = options?.body as FormData;
    expect(body.getAll('selected_fields')).toEqual(['purchase_price', 'property_address']);
    expect(body.get('file')).toBe(contract);
    screen.getAllByRole('checkbox').forEach((checkbox) => expect(checkbox).toBeDisabled());
    expect(screen.getByLabelText('Purchase contract')).toBeDisabled();
    const submit = screen.getByRole('button', { name: 'Extracting…' });
    expect(submit).toBeDisabled();
    expect(screen.getByRole('status')).toHaveTextContent('Extracting selected fields.');
    await user.click(submit);
    expect(fetchMock).toHaveBeenCalledTimes(1);

    await act(async () => resolve(json({ results: [foundPrice, missingAddress] })));
    const results = screen.getByRole('region', { name: 'Extraction results' });
    expect(within(results).getByText('UF 8.500')).toBeVisible();
    expect(within(results).getByText('Missing')).toBeVisible();
    expect(within(results).getAllByRole('term')).toHaveLength(2);
    expect(within(results).queryByText('Purchaser name')).not.toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveTextContent('1 found, 1 missing.');
    expect(screen.getByRole('button', { name: 'Extract fields' })).toBeEnabled();
  });

  it('keeps completed results attached to their request while preparing another', async () => {
    fetchMock.mockResolvedValueOnce(json({ results: [foundPrice] }));
    const user = await prepare();
    await user.click(screen.getByRole('button', { name: 'Extract fields' }));
    await screen.findByRole('region', { name: 'Extraction results' });
    await user.click(screen.getByRole('checkbox', { name: 'Purchase price' }));
    await user.click(screen.getByRole('checkbox', { name: 'Purchaser name' }));
    await user.upload(screen.getByLabelText('Purchase contract'), new File(['next'], 'next.pdf', { type: 'application/pdf' }));

    const results = screen.getByRole('region', { name: 'Extraction results' });
    expect(within(results).getByText('contract.pdf')).toBeVisible();
    expect(within(results).getByText('Purchase price')).toBeVisible();
    expect(within(results).getByText('UF 8.500')).toBeVisible();
    expect(within(results).queryByText('next.pdf')).not.toBeInTheDocument();
    expect(within(results).queryByText('Purchaser name')).not.toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('clears old results at submission, recovers from failure, and allows retry', async () => {
    let resolve!: (response: Response) => void;
    fetchMock.mockResolvedValueOnce(json({ results: [foundPrice] }));
    fetchMock.mockImplementationOnce(() => new Promise((done) => { resolve = done; }));
    fetchMock.mockResolvedValueOnce(json({ results: [missingAddress] }));
    const user = await prepare();
    await user.click(screen.getByRole('button', { name: 'Extract fields' }));
    await screen.findByText('UF 8.500');
    await user.click(screen.getByRole('checkbox', { name: 'Purchase price' }));
    await user.click(screen.getByRole('checkbox', { name: 'Property address' }));
    await user.click(screen.getByRole('button', { name: 'Extract fields' }));
    expect(screen.queryByRole('region', { name: 'Extraction results' })).not.toBeInTheDocument();
    await act(async () => resolve(json({ detail: 'Extraction failed. Please try again.' }, 500)));
    expect(screen.getByRole('alert')).toHaveTextContent('Extraction failed. Please try again.');
    expect(screen.queryByText('UF 8.500')).not.toBeInTheDocument();
    expect(screen.queryByText('Missing')).not.toBeInTheDocument();
    expect(screen.getByLabelText('Purchase contract')).toBeEnabled();
    await user.click(screen.getByRole('button', { name: 'Extract fields' }));
    expect(await screen.findByText('Missing')).toBeVisible();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect((fetchMock.mock.calls[2][1]?.body as FormData).getAll('selected_fields')).toEqual(['property_address']);
  });

  it.each([
    ['network failure', () => Promise.reject(new TypeError('Failed to fetch')), 'Could not reach the server. Check your connection and try again.'],
    ['empty gateway response', () => Promise.resolve(new Response(null, { status: 502 })), 'The server is unavailable. Please try again shortly.'],
    ['422 string detail', () => Promise.resolve(json({ detail: 'The PDF contains no extractable text. Please upload a text-based PDF.' }, 422)), 'The PDF contains no extractable text. Please upload a text-based PDF.'],
    ['422 list detail', () => Promise.resolve(json({ detail: [{ msg: 'Field required', loc: ['body', 'file'] }] }, 422)), 'Check the selected fields and file.'],
    ['server failure without detail', () => Promise.resolve(json({}, 500)), 'Extraction failed. Please try again.'],
    ['incomplete success response', () => Promise.resolve(json({ results: [] })), 'The server returned an unreadable response. Please try again.'],
  ])('handles %s without missing-field results and restores controls', async (_name, respond, message) => {
    fetchMock.mockImplementationOnce(respond);
    const user = await prepare();
    await user.click(screen.getByRole('button', { name: 'Extract fields' }));
    expect(await screen.findByRole('alert')).toHaveTextContent(message);
    expect(within(screen.getByRole('alert')).getByRole('heading')).toHaveTextContent('Something went wrong');
    expect(screen.queryByRole('region', { name: 'Extraction results' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Extract fields' })).toBeEnabled();
    expect(screen.getByLabelText('Purchase contract')).toBeEnabled();
    screen.getAllByRole('checkbox').forEach((checkbox) => expect(checkbox).toBeEnabled());
  });
});
