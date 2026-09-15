# Additional synthetic PDF fixtures

A–N are manual edge-case fixtures. They preserve the canonical Spanish contract structure, A4 page size, Helvetica fonts, synthetic-document notice, and signature blocks. All people, addresses, companies, and amounts are invented. These are well-formed, text-based PDFs; no OCR, malformed-file, or production-hardening cases are included.

Upload a PDF and select all four fields to compare with the table below. You can also select a subset: only those selected fields should appear. `missing` means the document was processed successfully but that field was not extracted.

## Cases

| PDF | Purpose |
| --- | --- |
| [A.pdf](A.pdf) | Complete contract with new synthetic values; accented purchaser name. |
| [B.pdf](B.pdf) | Explicit CLP price in the canonical price sentence. |
| [C.pdf](C.pdf) | Explicit USD price with thousands and decimal separators. |
| [D.pdf](D.pdf) | Address abbreviations and an extra sentence after the address; exclude that sentence. |
| [E.pdf](E.pdf) | Rename the price heading to Pago; the address must still be found. |
| [F.pdf](F.pdf) | Narrower text wrapping and extra spaces; normalize whitespace without losing values. |
| [G.pdf](G.pdf) | Ignore the preparation date, seller office address, and deposit in favor of the requested values. |
| [H.pdf](H.pdf) | Purchaser identity pending; other three fields remain extractable. |
| [I.pdf](I.pdf) | Total price pending, with a deposit present; do not substitute the deposit. |
| [J.pdf](J.pdf) | Signing date pending despite a dated introduction; do not substitute the introductory date. |
| [K.pdf](K.pdf) | Property address absent despite a seller office address. |
| [L.pdf](L.pdf) | Readable draft with all four requested values absent; expect four missing results, not a processing error. |
| [M.pdf](M.pdf) | Known limitation: bare $ does not identify a currency; price stays missing. |
| [N.pdf](N.pdf) | Known limitation: Firmado el día is outside the supported signing-date wording. |

## Expected results

These expectations were checked against the current extraction service when the fixtures were created. M and N deliberately exercise documented parser limits: a value is visible to a person but the supported rules do not extract it. The table describes current intended parser behavior, not general document understanding.

| PDF | Purchaser name | Purchase price | Contract date | Property address |
| --- | --- | --- | --- | --- |
| A | Valentina Isabel Muñoz Peña | UF 7.350 | 18 de octubre de 2026 | Pasaje Las Brisas 742, departamento 16, comuna de La Reina, Santiago |
| B | Valentina Isabel Muñoz Peña | CLP 187.500.000 | 18 de octubre de 2026 | Pasaje Las Brisas 742, departamento 16, comuna de La Reina, Santiago |
| C | Valentina Isabel Muñoz Peña | USD 215,750.50 | 18 de octubre de 2026 | Pasaje Las Brisas 742, departamento 16, comuna de La Reina, Santiago |
| D | Valentina Isabel Muñoz Peña | UF 7.350 | 18 de octubre de 2026 | Av. Los Canelos 925, Depto. 42, comuna de Ñuñoa, Santiago |
| E | Valentina Isabel Muñoz Peña | UF 7.350 | 18 de octubre de 2026 | Avda. Las Acacias 160, Dpto. 7, comuna de Macul, Santiago |
| F | Valentina Isabel Muñoz Peña | UF 7.350 | 18 de octubre de 2026 | Pasaje Las Brisas 742, departamento 16, comuna de La Reina, Santiago |
| G | Valentina Isabel Muñoz Peña | UF 7.350 | 18 de octubre de 2026 | Pasaje Las Brisas 742, departamento 16, comuna de La Reina, Santiago |
| H | **missing** | UF 7.350 | 18 de octubre de 2026 | Pasaje Las Brisas 742, departamento 16, comuna de La Reina, Santiago |
| I | Valentina Isabel Muñoz Peña | **missing** | 18 de octubre de 2026 | Pasaje Las Brisas 742, departamento 16, comuna de La Reina, Santiago |
| J | Valentina Isabel Muñoz Peña | UF 7.350 | **missing** | Pasaje Las Brisas 742, departamento 16, comuna de La Reina, Santiago |
| K | Valentina Isabel Muñoz Peña | UF 7.350 | 18 de octubre de 2026 | **missing** |
| L | **missing** | **missing** | **missing** | **missing** |
| M | Valentina Isabel Muñoz Peña | **missing** | 18 de octubre de 2026 | Pasaje Las Brisas 742, departamento 16, comuna de La Reina, Santiago |
| N | Valentina Isabel Muñoz Peña | UF 7.350 | **missing** | Pasaje Las Brisas 742, departamento 16, comuna de La Reina, Santiago |

These additional PDFs are for manual exploration and do not add parameterized cases to the automated backend or frontend suites. The three canonical fixtures remain unchanged.
