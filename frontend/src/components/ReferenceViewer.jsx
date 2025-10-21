import React, { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

export default function ReferenceViewer({ refType = "class" }) {
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/references?ref_type=${encodeURIComponent(refType)}`)
      .then((r) => r.json())
      .then((data) => {
        setItems(data || []);
        if ((data || []).length > 0) setSelected(data[0]);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [refType]);

  if (loading) return <div>Loading references...</div>;
  if (error) return <div>Error loading references: {error}</div>;

  return (
    <div style={{ display: "flex", gap: 16 }}>
      <aside style={{ width: 300 }}>
        <h3>{refType.charAt(0).toUpperCase() + refType.slice(1)} references</h3>
        <ul style={{ listStyle: "none", padding: 0 }}>
          {items.map((it) => (
            <li key={it.id} style={{ marginBottom: 8 }}>
              <button
                onClick={() => setSelected(it)}
                style={{ width: "100%", textAlign: "left" }}
              >
                {it.title}
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <main style={{ flex: 1 }}>
        {selected ? (
          <div>
            <h2>{selected.title}</h2>
            <ReactMarkdown>{selected.content || "*No content*"}</ReactMarkdown>
          </div>
        ) : (
          <div>No reference selected</div>
        )}
      </main>
    </div>
  );
}
