export const FIELDS = [
  { id: 'purchaser_name', label: 'Purchaser name' },
  { id: 'purchase_price', label: 'Purchase price' },
  { id: 'contract_date', label: 'Contract date' },
  { id: 'property_address', label: 'Property address' },
] as const;

export type FieldId = (typeof FIELDS)[number]['id'];
