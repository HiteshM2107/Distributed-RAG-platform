import { useState, useEffect } from "react";
import axios from "axios";
import {
  Line,
  Bar
} from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const API_BASE = "http://localhost:8000";

function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [chunks, setChunks] = useState([]);

  const [metricsRaw, setMetricsRaw] = useState([]);
  const [metricsComparison, setMetricsComparison] = useState([]);

  const [filterChunk, setFilterChunk] = useState("");
  const [filterTopK, setFilterTopK] = useState("");

  const [compareMode, setCompareMode] = useState("top_k");

  const [loadingUpload, setLoadingUpload] = useState(false);
  const [loadingQuery, setLoadingQuery] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");

  const [darkMode, setDarkMode] = useState(true);

  const theme = darkMode
    ? {
        background: "#0f172a",
        text: "#f1f5f9",
        card: "#1e293b"
      }
    : {
        background: "#f8fafc",
        text: "#0f172a",
        card: "#ffffff"
      };

  const uploadFile = async () => {
    if (!file) return;
    setLoadingUpload(true);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("chunk_size", 300);

    await axios.post(`${API_BASE}/upload`, formData);
    setLoadingUpload(false);
    alert("Upload complete");
  };

  const askQuestion = async () => {
    if (!token) {
      alert("Please login first");
      return;
    }
  
    setLoadingQuery(true);
  
    const res = await axios.post(
      `${API_BASE}/query`,
      {
        query,
        top_k: 3,
        chunk_size: 300
      },
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );
  
    setAnswer(res.data.answer);
    setChunks(res.data.retrieved_chunks);
  
    await loadRawMetrics();
    await loadComparisonMetrics();
  
    setLoadingQuery(false);
  };

  const login = async () => {
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);
  
    const res = await axios.post(`${API_BASE}/login`, formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });
  
    setToken(res.data.access_token);
  };

  const loadRawMetrics = async () => {
    const res = await axios.get(`${API_BASE}/metrics`);
    setMetricsRaw(res.data.data || []);
  };

  const loadComparisonMetrics = async () => {
    const res = await axios.get(`${API_BASE}/compare`, {
      params: {
        chunk_size: filterChunk || undefined,
        top_k: filterTopK || undefined
      }
    });

    setMetricsComparison(res.data.comparison || []);
  };

  useEffect(() => {
    loadRawMetrics();
    loadComparisonMetrics();
  }, []);

  const latencyChartData = {
    labels: metricsRaw.map(m => `Exp ${m[0]}`),
    datasets: [
      {
        label: "Total Latency (s)",
        data: metricsRaw.map(m => m[6]),
        borderColor: "#6366f1",
        backgroundColor: "#6366f1"
      }
    ]
  };

  const comparisonChartData = {
    labels: metricsComparison.map(m =>
      compareMode === "top_k"
        ? `k=${m[1]}`
        : `chunk=${m[0]}`
    ),
    datasets: [
      {
        label: "Avg Total Latency (s)",
        data: metricsComparison.map(m => m[2]),
        backgroundColor: "#22c55e"
      }
    ]
  };

  return (
    <div
      style={{
        background: theme.background,
        color: theme.text,
        minHeight: "100vh",
        width: "100vw",
        display: "flex",
        flexDirection: "column", 
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "Inter, sans-serif"
      }}
    >
      {!token ? (
        // LOGIN SCREEN ONLY
        <div
          style={{
            background: theme.card,
            padding: "40px",
            borderRadius: "16px",
            width: "400px",
            boxShadow: "0 10px 30px rgba(0,0,0,0.3)"
          }}
        >
          <h2 style={{ marginBottom: "20px" }}>Login</h2>
  
          <input
            placeholder="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
            style={{ width: "100%", marginBottom: "10px", padding: "8px" }}
          />
  
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            style={{ width: "100%", marginBottom: "15px", padding: "8px" }}
          />
  
          <button
            onClick={login}
            style={{ width: "100%", padding: "10px" }}
          >
            Login
          </button>
        </div>
      ) : (
        // MAIN APP
        <div style={{ width: "100%", maxWidth: "1200px", padding: "40px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "20px" }}>
            <h1>Distributed RAG Platform</h1>
            <button onClick={() => setToken("")}>Logout</button>
          </div>
          <div style={{ background: theme.card, padding: "20px", borderRadius: "12px", marginBottom: "20px" }}>
            <h2>Upload PDF</h2>
            <input type="file" onChange={e => setFile(e.target.files[0])} />
            <button onClick={uploadFile} style={{ marginLeft: "10px" }}>
              {loadingUpload ? "Uploading..." : "Upload"}
            </button>
          </div>

          <div style={{ background: theme.card, padding: "20px", borderRadius: "12px", marginBottom: "20px" }}>
            <h2>Ask Question</h2>
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              style={{ width: "60%", padding: "8px" }}
            />
            <button onClick={askQuestion} style={{ marginLeft: "10px" }}>
              {loadingQuery ? "Processing..." : "Ask"}
            </button>

            {answer && (
              <>
                <h3 style={{ marginTop: "20px" }}>Answer</h3>
                <p>{answer}</p>

                <h3>Retrieved Context</h3>
                {chunks.map((chunk, i) => (
                  <div
                    key={i}
                    style={{
                      background: darkMode ? "#334155" : "#e2e8f0",
                      padding: "12px",
                      borderRadius: "8px",
                      marginBottom: "10px"
                    }}
                  >
                    {chunk}
                  </div>
                ))}
              </>
            )}
          </div>

          <div style={{ background: theme.card, padding: "20px", borderRadius: "12px", marginBottom: "20px" }}>
            <h2>Filter Experiments</h2>

            <label>Chunk Size:</label>
            <input
              type="number"
              value={filterChunk}
              onChange={e => setFilterChunk(e.target.value)}
              style={{ marginRight: "20px", marginLeft: "10px" }}
            />

            <label>Top K:</label>
            <input
              type="number"
              value={filterTopK}
              onChange={e => setFilterTopK(e.target.value)}
              style={{ marginLeft: "10px", marginRight: "20px" }}
            />

            <button onClick={loadComparisonMetrics}>Apply Filter</button>
          </div>

          <div style={{ background: theme.card, padding: "20px", borderRadius: "12px", marginBottom: "20px" }}>
            <h2>Latency Over Experiments</h2>
            <Line data={latencyChartData} />
          </div>

          <div style={{ background: theme.card, padding: "20px", borderRadius: "12px" }}>
            <h2>Experiment Comparison</h2>

            <select
              value={compareMode}
              onChange={e => setCompareMode(e.target.value)}
              style={{ marginBottom: "15px" }}
            >
              <option value="top_k">Compare by Top-K</option>
              <option value="chunk_size">Compare by Chunk Size</option>
            </select>

            <Bar data={comparisonChartData} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;