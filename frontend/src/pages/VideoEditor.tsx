import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ArrowLeft, Send, Sparkles } from "lucide-react";
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}
const VideoEditor = () => {
  const [messages, setMessages] = useState<Message[]>([{
    id: "1",
    role: "assistant",
    content: "Your video on 'Introduction to Binary Search Trees' has been generated! You can now watch it or ask me to make any changes."
  }]);
  const [inputValue, setInputValue] = useState("");
  const handleSendMessage = () => {
    if (!inputValue.trim()) return;
    const newMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue
    };
    setMessages([...messages, newMessage]);
    setInputValue("");

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I'll update the video with your requested changes. Please give me a moment..."
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };
  return <div className="min-h-screen bg-gradient-hero relative overflow-hidden">
      {/* Subtle background pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
        backgroundImage: `repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            hsl(var(--primary)) 2px,
            hsl(var(--primary)) 4px
          )`
      }} />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-border/50 bg-card/30 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2 text-foreground hover:text-primary transition-colors">
              <ArrowLeft className="w-5 h-5" />
              <span className="font-semibold">Back to Home</span>
            </Link>
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              <span className="text-foreground font-semibold">AI Video Editor</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="relative z-10 container mx-auto px-6 py-8 h-[calc(100vh-80px)]">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
          {/* Left Panel - Chat Interface */}
          <div className="bg-card/50 backdrop-blur-sm rounded-2xl border border-border/50 shadow-elevated flex flex-col overflow-hidden">
            <div className="px-6 py-4 border-b border-border/50">
              <h2 className="text-xl font-semibold text-foreground">Edit Your Video</h2>
              <p className="text-sm text-muted-foreground mt-1">
                Chat with AI to refine your educational video
              </p>
            </div>

            {/* Messages */}
            <ScrollArea className="flex-1 px-6 py-4">
              <div className="space-y-4">
                {messages.map(message => <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.role === "user" ? "bg-gradient-primary text-primary-foreground" : "bg-muted/50 text-foreground border border-border/30"}`}>
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    </div>
                  </div>)}
              </div>
            </ScrollArea>

            {/* Input Area */}
            <div className="p-4 border-t border-border/50 bg-card/30">
              <div className="flex gap-2">
                <Input value={inputValue} onChange={e => setInputValue(e.target.value)} onKeyPress={e => e.key === "Enter" && handleSendMessage()} placeholder="Ask to change voice, add visuals, adjust pace..." className="flex-1 bg-background/50 border-border/50 focus-visible:ring-primary" />
                <Button onClick={handleSendMessage} variant="hero" size="icon" className="shrink-0">
                  <Send className="w-4 h-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Example: "Change the voice to be slower" or "Add more visual examples"
              </p>
            </div>
          </div>

          {/* Right Panel - Video Player */}
          <div className="bg-card/50 backdrop-blur-sm rounded-2xl border border-border/50 shadow-elevated overflow-hidden flex flex-col">
            <div className="px-6 py-4 border-b border-border/50">
              <h2 className="text-xl font-semibold text-foreground">Generated Video</h2>
              <p className="text-sm text-muted-foreground mt-1">​View your current video below</p>
            </div>

            {/* Video Container */}
            <div className="flex-1 bg-background/30 flex items-center justify-center p-6">
              <div className="w-full aspect-video bg-gradient-to-br from-background to-muted/20 rounded-xl border border-border/30 shadow-glow flex items-center justify-center">
                <div className="text-center space-y-4">
                  <div className="w-20 h-20 mx-auto rounded-full bg-gradient-primary flex items-center justify-center animate-pulse">
                    <Sparkles className="w-10 h-10 text-primary-foreground" />
                  </div>
                  <div>
                    <p className="text-foreground font-semibold">Video Player</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      Your generated video will appear here
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Video Controls Info */}
            <div className="px-6 py-4 border-t border-border/50 bg-card/30">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Duration: 3:45</span>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    Download
                  </Button>
                  <Button variant="secondary" size="sm">
                    Share
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>;
};
export default VideoEditor;