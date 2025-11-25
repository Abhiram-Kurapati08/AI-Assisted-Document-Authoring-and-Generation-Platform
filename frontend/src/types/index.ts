export type DocumentType = "docx" | "pptx";

export type Project = {
  id: string;
  title: string;
  doc_type: DocumentType;
  topic_prompt?: string | null;
  user_id: string;
  created_at: string;
  updated_at?: string | null;
  section_count?: number;
};

export type ProjectListResponse = {
  items: Project[];
  total: number;
  page: number;
  size: number;
};

export type Section = {
  id: string;
  project_id: string;
  title: string;
  content: string;
  idx: number;
  initial_generated: boolean;
  revision_count: number;
  comment_count: number;
  created_at: string;
  updated_at?: string | null;
};

export type SectionListResponse = {
  items: Section[];
  total: number;
  page: number;
  size: number;
};

