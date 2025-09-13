import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

export function LoadingPage() {
  const [searchParams] = useSearchParams();
  const userId = searchParams.get("user_id");
  const [status, setStatus] = useState({ gmail: "PENDING", telegram: "PENDING" });
  const navigate = useNavigate();
  const API_URL = import.meta.env.VITE_API_URL;
  const wsURL = API_URL.replace("https://", "wss://").replace("http://", "ws://");

  useEffect(() => {
    const ws = new WebSocket(`${wsURL}/auth/telegram/task-status`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.user_id === userId) {
        setStatus((prev) => {
          const updated = { ...prev, [data.task]: data.status };

          if (updated.gmail === "SUCCESS" && updated.telegram === "SUCCESS") {
            navigate("/home");
          }

          return updated;
        });
      }
    };

    return () => {
      ws.close();
    };
  }, [userId, navigate]);

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100vh" }}>
      <h1>Processing your messages...</h1>
      <p>Gmail: {status.gmail}</p>
      <p>Telegram: {status.telegram}</p>
      <div style={{ marginTop: 20 }}>
        <div className="loader" />
      </div>
      <style>{`
        .loader {
          border: 6px solid #f3f3f3;
          border-top: 6px solid #3498db;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          animation: spin 1s linear infinite;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}

