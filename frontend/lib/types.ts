export type OperatorRun = {
  id: number;
  source_id: number;
  source_name: string;
  source_system: string;
  run_type: string;
  trigger_type: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  records_fetched_count: number;
  duplicates_detected_count: number;
  error_message: string | null;
};

export type OperatorSourceSummary = {
  id: number;
  source_name: string;
  source_system: string;
  acquisition_mode: string;
  auth_type: string;
  enabled: boolean;
  schedule: string | null;
  parser_name: string | null;
  dedupe_keys: string[] | null;
  notes: string | null;
  config_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  workflow_label: string;
  primary_action_label: string;
  supports_test_connection: boolean;
  supports_direct_trigger: boolean;
  supports_manual_upload: boolean;
  supports_scheduler: boolean;
  special_actions: string[];
  latest_run: OperatorRun | null;
  raw_object_count: number;
  record_count: number;
  gift_record_count: number;
  raw_object_types: string[];
  record_status_values: string[];
  latest_record_date: string | null;
};

export type OperatorConsoleSummary = {
  total_sources: number;
  total_records: number;
  total_gift_records: number;
  total_raw_objects: number;
  latest_run_at: string | null;
};

export type OperatorConsoleState = {
  summary: OperatorConsoleSummary;
  sources: OperatorSourceSummary[];
  recent_runs: OperatorRun[];
};

export type OperatorRecord = {
  id: number;
  raw_object_id: number;
  source_id: number;
  source_name: string;
  record_type: string | null;
  source_record_id: string | null;
  source_parent_id: string | null;
  gift_id: string | null;
  source_channel: string | null;
  source_system: string | null;
  source_file_id: string | null;
  primary_name: string | null;
  primary_email: string | null;
  donor_name: string | null;
  donor_email: string | null;
  company_name: string | null;
  amount: string | number | null;
  currency: string | null;
  record_date: string | null;
  gift_date: string | null;
  payment_type: string | null;
  gift_type: string | null;
  campaign_id: string | null;
  campaign_name: string | null;
  challenge_id: string | null;
  challenge_name: string | null;
  related_entity_id: string | null;
  related_entity_name: string | null;
  participant_id: string | null;
  participant_name: string | null;
  team_id: string | null;
  team_name: string | null;
  charity_id: string | null;
  receipt_number: string | null;
  memo: string | null;
  raw_payload_ref: string | null;
  status: string | null;
  duplicate_status: string | null;
  confidence_score: number | null;
  extra_metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type RecordFilters = {
  sourceId?: number;
  recordType?: string;
  status?: string;
  search?: string;
  limit?: number;
};

export type SourceAction = "test" | "paid" | "supporters" | "full";
