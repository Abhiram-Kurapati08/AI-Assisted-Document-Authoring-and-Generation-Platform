import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../lib/api";
import type { Project, Section, SectionListResponse } from "../types";

const emptySection = {
  title: "",
  content: "",
  idx: 0,
};

const ProjectDetailPage = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [sections, setSections] = useState<Section[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sectionForm, setSectionForm] = useState(emptySection);
  const [savingSection, setSavingSection] = useState(false);
  const [selectedSection, setSelectedSection] = useState<Section | null>(null);
  const [refinePrompt, setRefinePrompt] = useState("");
  const [generatePrompt, setGeneratePrompt] = useState("");
  const [llmBusy, setLlmBusy] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState<"docx" | "pptx" | "txt">("docx");

  const fetchProject = async () => {
    if (!projectId) return;
    try {
      const { data } = await api.get<Project>(`/projects/${projectId}`);
      setProject(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Unable to load project");
    }
  };

  const fetchSections = async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get<SectionListResponse>(
        `/projects/${projectId}/sections/`,
        { params: { limit: 100 } }
      );
      setSections(data.items ?? []);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Unable to load sections");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProject();
    fetchSections();
  }, [projectId]);

  useEffect(() => {
    if (sections.length === 0) {
      setSelectedSection(null);
      return;
    }
    setSelectedSection((prev) => {
      if (!prev) return sections[0];
      const updated = sections.find((section) => section.id === prev.id);
      return updated ?? sections[0];
    });
  }, [sections]);

  const handleSectionCreate = async (event: FormEvent) => {
    event.preventDefault();
    if (!projectId) return;
    setSavingSection(true);
    try {
      await api.post(`/projects/${projectId}/sections/`, {
        title: sectionForm.title,
        content: sectionForm.content,
        idx: sectionForm.idx,
      });
      setSectionForm(emptySection);
      await fetchSections();
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Unable to create section");
    } finally {
      setSavingSection(false);
    }
  };

  const handleSectionUpdate = async (section: Section) => {
    if (!projectId) return;
    setSavingSection(true);
    try {
      await api.put(`/projects/${projectId}/sections/${section.id}`, {
        title: section.title,
        content: section.content,
      });
      await fetchSections();
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Unable to update section");
    } finally {
      setSavingSection(false);
    }
  };

  const handleGenerate = async () => {
    if (!projectId || !selectedSection) return;
    setLlmBusy(true);
    setError(null);
    try {
      const { data } = await api.post(
        `/projects/${projectId}/sections/${selectedSection.id}/refine/generate`,
        {
          prompt: generatePrompt || selectedSection.title,
          temperature: 0.7,
          max_tokens: 800,
        }
      );
      setSelectedSection(data);
      await fetchSections();
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Unable to generate content");
    } finally {
      setLlmBusy(false);
    }
  };

  const handleRefine = async () => {
    if (!projectId || !selectedSection) return;
    setLlmBusy(true);
    setError(null);
    try {
      const { data } = await api.post(
        `/projects/${projectId}/sections/${selectedSection.id}/refine/`,
        {
          refine_instruction: refinePrompt,
          prompt: selectedSection.content,
          preserve_formatting: true,
          temperature: 0.6,
          max_tokens: 800,
        }
      );
      setSelectedSection(data);
      await fetchSections();
      setRefinePrompt("");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Unable to refine content");
    } finally {
      setLlmBusy(false);
    }
  };

  const handleExport = async () => {
    if (!projectId) return;
    setExporting(true);
    setError(null);
    try {
      const authHeader =
        typeof api.defaults.headers.common.Authorization === "string"
          ? api.defaults.headers.common.Authorization
          : undefined;
      const response = await fetch(
        `${import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000"}/projects/${projectId}/export/?format=${exportFormat}`,
        {
          headers: authHeader ? { Authorization: authHeader } : undefined,
        }
      );
      if (!response.ok) throw new Error("Export failed");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${project?.title ?? "document"}.${exportFormat}`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.message ?? "Unable to download export");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="project-detail">
      <header className="panel span-2">
        <Link to="/projects" className="breadcrumb">
          ← Back to projects
        </Link>
        {project ? (
          <>
            <h2>{project.title}</h2>
            <p className="muted">{project.topic_prompt || "No topic provided"}</p>
            <div className="project-meta">
              <span className="badge">{project.doc_type.toUpperCase()}</span>
              <span>{project.section_count ?? 0} sections</span>
              <button type="button" onClick={handleExport} disabled={exporting}>
                {exporting ? "Exporting..." : `Export ${exportFormat.toUpperCase()}`}
              </button>
              <select
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value as any)}
              >
                <option value="docx">DOCX</option>
                <option value="pptx">PPTX</option>
                <option value="txt">TXT</option>
              </select>
            </div>
          </>
        ) : (
          <p>Loading project...</p>
        )}
      </header>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Sections</h3>
            <p>Click a section to edit or refine.</p>
          </div>
        </div>
        {loading ? (
          <p>Loading sections...</p>
        ) : sections.length === 0 ? (
          <p>No sections yet.</p>
        ) : (
          <ul className="section-list">
            {sections.map((section) => (
              <li key={section.id}>
                <button
                  type="button"
                  className={section.id === selectedSection?.id ? "active" : ""}
                  onClick={() => setSelectedSection(section)}
                >
                  <strong>{section.title}</strong>
                  <span>{section.initial_generated ? "AI" : "Manual"}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="panel span-2">
        <div className="panel-header">
          <div>
            <h3>Section editor</h3>
            <p>Update content or send to the LLM for refinement.</p>
          </div>
        </div>
        {selectedSection ? (
          <div className="editor">
            <input
              type="text"
              value={selectedSection.title}
              onChange={(e) =>
                setSelectedSection((prev) =>
                  prev ? { ...prev, title: e.target.value } : prev
                )
              }
            />
            <textarea
              rows={12}
              value={selectedSection.content || ""}
              onChange={(e) =>
                setSelectedSection((prev) =>
                  prev ? { ...prev, content: e.target.value } : prev
                )
              }
            />
            <div className="editor-actions">
              <button
                type="button"
                disabled={savingSection}
                onClick={() =>
                  selectedSection && handleSectionUpdate(selectedSection)
                }
              >
                {savingSection ? "Saving..." : "Save"}
              </button>
              <div className="llm-controls">
                <input
                  type="text"
                  placeholder="Generation prompt"
                  value={generatePrompt}
                  onChange={(e) => setGeneratePrompt(e.target.value)}
                />
                <button type="button" onClick={handleGenerate} disabled={llmBusy}>
                  Generate
                </button>
                <input
                  type="text"
                  placeholder="Refinement instruction"
                  value={refinePrompt}
                  onChange={(e) => setRefinePrompt(e.target.value)}
                />
                <button type="button" onClick={handleRefine} disabled={llmBusy}>
                  Refine
                </button>
              </div>
            </div>
          </div>
        ) : (
          <p>Select a section to begin editing.</p>
        )}
      </section>

      <section className="panel span-2">
        <div className="panel-header">
          <div>
            <h3>Add manual section</h3>
            <p>Insert custom sections to complement AI output.</p>
          </div>
        </div>
        <form className="form inline" onSubmit={handleSectionCreate}>
          <input
            type="text"
            placeholder="Title"
            value={sectionForm.title}
            onChange={(e) =>
              setSectionForm((prev) => ({ ...prev, title: e.target.value }))
            }
            required
          />
          <textarea
            rows={4}
            placeholder="Content"
            value={sectionForm.content}
            onChange={(e) =>
              setSectionForm((prev) => ({ ...prev, content: e.target.value }))
            }
          />
          <input
            type="number"
            min={0}
            value={sectionForm.idx}
            onChange={(e) =>
              setSectionForm((prev) => ({ ...prev, idx: Number(e.target.value) }))
            }
          />
          <button type="submit" disabled={savingSection}>
            {savingSection ? "Adding..." : "Add section"}
          </button>
        </form>
      </section>

      {error && <p className="error span-2">{error}</p>}
    </div>
  );
};

export default ProjectDetailPage;

