import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";
import api from "../lib/api";
import type { Project, ProjectListResponse } from "../types";

const defaultProjectForm = {
  title: "",
  doc_type: "docx",
  topic_prompt: "",
};

const ProjectsPage = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState(defaultProjectForm);
  const [creating, setCreating] = useState(false);
  const [generator, setGenerator] = useState({
    projectId: "",
    num_sections: 5,
    include_outline: true,
    outline_format: "",
  });
  const [generating, setGenerating] = useState(false);
  const [search, setSearch] = useState("");

  const filteredProjects = useMemo(() => {
    if (!search) return projects;
    return projects.filter((project) =>
      project.title.toLowerCase().includes(search.toLowerCase())
    );
  }, [projects, search]);

  const fetchProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get<ProjectListResponse>("/projects/", {
        params: { limit: 50 },
      });
      setProjects(data.items ?? []);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Unable to load projects");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault();
    setCreating(true);
    try {
      await api.post("/projects/", {
        title: form.title,
        doc_type: form.doc_type,
        topic_prompt: form.topic_prompt || null,
      });
      setForm(defaultProjectForm);
      await fetchProjects();
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Unable to create project");
    } finally {
      setCreating(false);
    }
  };

  const handleGenerate = async (event: FormEvent) => {
    event.preventDefault();
    if (!generator.projectId) {
      setError("Select a project first");
      return;
    }
    setGenerating(true);
    setError(null);
    try {
      await api.post(`/projects/${generator.projectId}/generate`, {
        num_sections: generator.num_sections,
        include_outline: generator.include_outline,
        outline_format: generator.outline_format || null,
      });
      await fetchProjects();
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Unable to generate content");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="grid">
      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Create a project</h2>
            <p>Define the structure and topic for your document.</p>
          </div>
        </div>
        <form className="form" onSubmit={handleCreate}>
          <label>
            Title
            <input
              type="text"
              value={form.title}
              onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
              required
            />
          </label>
          <label>
            Document type
            <select
              value={form.doc_type}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, doc_type: e.target.value }))
              }
            >
              <option value="docx">Word (.docx)</option>
              <option value="pptx">PowerPoint (.pptx)</option>
            </select>
          </label>
          <label>
            Topic prompt
            <textarea
              value={form.topic_prompt}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, topic_prompt: e.target.value }))
              }
              placeholder="Describe the document you want to generate..."
              rows={3}
            />
          </label>
          <button type="submit" disabled={creating}>
            {creating ? "Creating..." : "Create project"}
          </button>
        </form>
      </section>

      <section className="panel">
          <div>
            <h2>Generate outline & sections</h2>
            <p>Use the LLM to scaffold a project in one click.</p>
          </div>
        
        <form className="form" onSubmit={handleGenerate}>
          <label>
            Project
            <select
              value={generator.projectId}
              onChange={(e) =>
                setGenerator((prev) => ({ ...prev, projectId: e.target.value }))
              }
              required
            >
              <option value="">Select project...</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            Number of sections
            <input
              type="number"
              min={1}
              max={20}
              value={generator.num_sections}
              onChange={(e) =>
                setGenerator((prev) => ({
                  ...prev,
                  num_sections: Number(e.target.value),
                }))
              }
            />
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={generator.include_outline}
              onChange={(e) =>
                setGenerator((prev) => ({
                  ...prev,
                  include_outline: e.target.checked,
                }))
              }
            />
            Include outline
          </label>
          <label>
            Outline format
            <input
              type="text"
              value={generator.outline_format}
              onChange={(e) =>
                setGenerator((prev) => ({
                  ...prev,
                  outline_format: e.target.value,
                }))
              }
              placeholder="Optional e.g. I. A. 1."
            />
          </label>
          <button type="submit" disabled={generating}>
            {generating ? "Generating..." : "Generate content"}
          </button>
        </form>
      </section>

      <section className="panel span-2">
        <div className="panel-header">
          <div>
            <h2>Your projects</h2>
            <p>Track progress and access sections.</p>
          </div>
          <input
            type="search"
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        {error && <p className="error">{error}</p>}
        {loading ? (
          <p>Loading projects...</p>
        ) : filteredProjects.length === 0 ? (
          <p>No projects yet.</p>
        ) : (
          <div className="project-grid">
            {filteredProjects.map((project) => (
              <article key={project.id} className="project-card">
                <header>
                  <h3>{project.title}</h3>
                  <span className="badge">{project.doc_type.toUpperCase()}</span>
                </header>
                <p className="muted small">{project.topic_prompt || "No topic provided"}</p>
                <footer>
                  <span>{project.section_count ?? 0} sections</span>
                  <Link to={`/projects/${project.id}`}>Open</Link>
                </footer>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default ProjectsPage;

