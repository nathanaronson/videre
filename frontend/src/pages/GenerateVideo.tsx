import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, Sparkles, Video, CheckCircle2 } from "lucide-react";

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
    {
      id: "video_generation_start",
      label: "Starting video generation...",
      status: "pending",
    },
    {
      id: "video_generation_manim_generated",
      label: "Manim code generated.",
      status: "pending",
    },
    {
      id: "video_generation_rendering_complete",
      label: "Video generation rendering complete.",
      status: "pending",
    },
    { id: "saving_complete", label: "Video successfully.", status: "pending" },
    { id: "url_created", label: "Ready to show!", status: "pending" },
  ]);
  const [error, setError] = useState<string | null>(null);

  const generateVideo = useCallback(async () => {
    try {
      // Make SSE request to backend
      const response = await fetch("http://localhost:8000/api/integrate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic }),
      });

      if (!response.ok) {
        throw new Error("Failed to start video generation");
      }

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      // Start analyzing step
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
        buffer = lines.pop() || ""; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const eventData = JSON.parse(line.slice(6));
              const eventType = eventData.type;
              const eventMessage = eventData.message || "";

              console.log("SSE Event:", eventType, eventData);

              // Handle different event types
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
                  // Update status message and progress steps
                  setSteps((prev) =>
                    prev.map((step, idx) => ({
                      ...step,
                      status:
                        idx === 1 || idx === 0
                          ? "completed"
                          : idx === 2
                          ? "processing"
                          : step.status,
                    }))
                  );
                  break;

                case "video_generation_rendering_complete":
                  // Update status message and progress steps
                  setSteps((prev) =>
                    prev.map((step, idx) => ({
                      ...step,
                      status:
                        idx === 2
                          ? "completed"
                          : idx === 3
                          ? "processing"
                          : step.status,
                    }))
                  );
                  break;

                case "saving_complete":
                  // Update status message and progress steps
                  setSteps((prev) =>
                    prev.map((step, idx) => ({
                      ...step,
                      status:
                        idx === 3
                          ? "completed"
                          : idx === 4
                          ? "processing"
                          : step.status,
                    }))
                  );
                  break;

                case "complete":
                  // Mark all steps as completed
                  setSteps((prev) =>
                    prev.map((step) => ({
                      ...step,
                      status: "completed",
                    }))
                  );

                  // Use the video URL from the event
                  if (eventData.video_url) {
                    setVideoURL(eventData.video_url);

                    // Navigate to video display after a short delay
                    setTimeout(() => {
                      navigate("/video");
                    }, 1500);
                  }
                  break;

                case "error":
                  setError(
                    eventData.message ||
                      "An error occurred during video generation"
                  );
                  break;
              }
            } catch (parseError) {
              console.error("Error parsing SSE event:", parseError, line);
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      console.error("Video generation error:", err);
    }
  }, [topic, navigate]);

  useEffect(() => {
    if (!topic) {
      navigate("/");
      return;
    }

    // Start the video generation process
    generateVideo();
  }, [topic, navigate, generateVideo]);

  const getStepIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case "processing":
        return <Loader2 className="w-5 h-5 text-primary animate-spin" />;
      default:
        return <div className="w-5 h-5 rounded-full border-2 border-muted" />;
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-destructive/10 border border-destructive rounded-lg p-6 mb-4">
            <p className="text-destructive font-semibold mb-2">Error</p>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
          <button
            onClick={() => navigate("/")}
            className="text-primary hover:underline"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="max-w-2xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 mb-4">
            <Sparkles className="w-8 h-8 text-primary animate-pulse" />
            <Video className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-3xl font-bold mb-2">Creating Your Video</h1>
          <p className="text-muted-foreground">
            Generating educational content about:{" "}
            <span className="font-semibold text-foreground">{topic}</span>
          </p>
        </div>

        {/* Progress Steps */}
        <div className="bg-card border border-border rounded-2xl p-8 shadow-lg">
          <div className="space-y-4">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className="flex items-center gap-4 transition-all duration-300"
              >
                <div className="flex-shrink-0">{getStepIcon(step.status)}</div>
                <div className="flex-1">
                  <p
                    className={`text-sm font-medium ${
                      step.status === "completed"
                        ? "text-muted-foreground line-through"
                        : step.status === "processing"
                        ? "text-primary"
                        : "text-muted-foreground"
                    }`}
                  >
                    {step.label}
                  </p>
                </div>
                {step.status === "processing" && (
                  <div className="flex-shrink-0">
                    <div className="flex gap-1">
                      <div
                        className="w-2 h-2 bg-primary rounded-full animate-bounce"
                        style={{ animationDelay: "0ms" }}
                      />
                      <div
                        className="w-2 h-2 bg-primary rounded-full animate-bounce"
                        style={{ animationDelay: "150ms" }}
                      />
                      <div
                        className="w-2 h-2 bg-primary rounded-full animate-bounce"
                        style={{ animationDelay: "300ms" }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Progress Bar */}
          <div className="mt-8">
            <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
              <div
                className="bg-gradient-to-r from-primary to-primary/60 h-full transition-all duration-500 ease-out"
                style={{
                  width: `${
                    (steps.filter((s) => s.status === "completed").length /
                      steps.length) *
                    100
                  }%`,
                }}
              />
            </div>
            <p className="text-xs text-muted-foreground text-center mt-2">
              {Math.round(
                (steps.filter((s) => s.status === "completed").length /
                  steps.length) *
                  100
              )}
              % complete
            </p>
          </div>
        </div>

        {/* Fun fact or tip while waiting */}
        <div className="mt-8 text-center">
          <p className="text-sm text-muted-foreground italic">
            This usually takes 30-60 seconds. Hang tight!
          </p>
        </div>
      </div>
    </div>
  );
};

export default GenerateVideo;
