export type CorrectionItem = {
  id: string;
  conditionCode: string;
  severityCode?: string;
  narrativeText?: string;
  scope?: string;
  viewName?: string;
  sectionName?: string;
  uiFieldName?: string;
  uiLabel?: string;
  recordId?: string;
  requestLineNumber?: number;
  requestLineNo?: string;
  fieldName?: string;
  fieldStart?: number;
  fieldEnd?: number;
  currentValue?: string;
  correctedValue?: string;
  status: string;
  validation: Record<string, unknown>;
};

export type CreateSessionResponse = {
  sessionId: string;
  entryNumber?: string;
  status: string;
  corrections: CorrectionItem[];
};
