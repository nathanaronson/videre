import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, Check } from "lucide-react";

interface GenerationStep {
  id: string;
  label: string;
  status: "pending" | "processing" | "completed";
}

const GenerateVideo = ({
  topic,
  setVideoURL,
}: {
  topic: string;
  setVideoURL: any;
}) => {
  const navigate = useNavigate();

  const [steps, setSteps] = useState<GenerationStep[]>([
    { id: "video_generation_start", label: "Starting", status: "pending" },
    { id: "video_generation_manim_generated", label: "Creating animations", status: "pending" },
    { id: "video_generation_rendering_complete", label: "Rendering", status: "pending" },
    { id: "saving_complete", label: "Saving", status: "pending" },
    { id: "url_created", label: "Finishing up", status: "pending" },
  ]);
  const [error, setError] = useState<string | null>(null);

  const generateVideo = useCallback(async () => {
    try {
      const response = await fetch("http://localhost:8000/api/integrate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
      });

      if (!response.ok) throw new Error("Failed to start generation");
      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      setSteps((prev) =>
        prev.map((step, idx) => ({
          ...step,
          status: idx === 0 ? "processing" : "pending",
        }))
      );

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const eventData = JSON.parse(line.slice(6));
              const eventType = eventData.type;

              switch (eventType) {
                case "video_generation_start":
                  setSteps((prev) =>
                    prev.map((step, idx) => ({
                      ...step,
                      status: idx === 0 ? "processing" : "pending",
                    }))
                  );
                  break;
                case "video_generation_manim_generated":
                  setSteps((prev) =>
                    prev.map((step, idx) => ({
                      ...step,
                      status: idx <= 1 ? "completed" : idx === 2 ? "processing" : step.status,
                    }))
                  );
                  break;
                case "video_generation_rendering_complete":
                  setSteps((prev) =>
                    prev.map((step, idx) => ({
                      ...step,
                      status: idx === 2 ? "completed" : idx === 3 ? "processing" : step.status,
                    }))
                  );
                  break;
                case "saving_complete":
                  setSteps((prev) =>
                    prev.map((step, idx) => ({
                      ...step,
                      status: idx === 3 ? "completed" : idx === 4 ? "processing" : step.status,
                    }))
                  );
                  break;
                case "complete":
                  setSteps((prev) => prev.map((step) => ({ ...step, status: "completed" })));
                  if (eventData.video_url) {
                    setVideoURL(eventData.video_url);
                    setTimeout(() => navigate("/video"), 800);
                  }
                  break;
                case "error":
                  setError(eventData.message || "Generation failed");
                  break;
              }
            } catch (e) {
              console.error("Parse error:", e);
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    }
  }, [topic, navigate, setVideoURL]);

  useEffect(() => {
    if (!topic) {
      navigate("/");
      return;
    }
    generateVideo();
  }, [topic, navigate, generateVideo]);

  if (error) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center px-6">
        <p className="text-muted-foreground mb-4">{error}</p>
        <button
          onClick={() => navigate("/")}
          className="text-sm text-foreground hover:opacity-70"
        >
          Try again
        </button>
      </div>
    );
  }

  const completedCount = steps.filter((s) => s.status === "completed").length;
  const progress = (completedCount / steps.length) * 100;

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm">
        {/* Topic */}
        <p className="text-sm text-muted-foreground mb-2">Generating</p>
        <h1 className="text-xl font-semibold tracking-tight mb-8 line-clamp-2">
          {topic}
        </h1>

        {/* Steps */}
        <div className="space-y-3 mb-8">
          {steps.map((step) => (
            <div key={step.id} className="flex items-center gap-3">
              <div className="w-5 h-5 flex items-center justify-center">
                {step.status === "completed" ? (
                  <Check className="w-4 h-4 text-foreground" />
                ) : step.status === "processing" ? (
                  <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
                ) : (
                  <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/30" />
                )}
              </div>
              <span
                className={`text-sm ${
                  step.status === "completed"
                    ? "text-muted-foreground"
                    : step.status === "processing"
                    ? "text-foreground"
                    : "text-muted-foreground/50"
                }`}
              >
                {step.label}
              </span>
            </div>
          ))}
        </div>

        {/* Progress bar */}
        <div className="w-full h-1 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-foreground transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default GenerateVideo;
