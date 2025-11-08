import os
import subprocess
import tempfile
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")


from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
from manim_voiceover.services.elevenlabs import ElevenLabsService
import numpy as np

class GeneratedScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(ElevenLabsService(api_key=ELEVEN_API_KEY, voice_id="29vD33N1CtxCmqQRPOHJ"))

        with self.voiceover(text="Imagine you're planning a road trip and want to find the shortest route to your destination. How does your GPS figure that out so quickly? The answer is Dijkstra's Algorithm.") as tracker:
            title = Text("Dijkstra's Algorithm", font_size=56, gradient=(BLUE, GREEN))
            title.to_edge(UP)
            self.play(Write(title))
            self.wait(0.5)
            
            car = SVGMobject("car").scale(0.3) if False else Circle(radius=0.2, color=RED, fill_opacity=1)
            destination = Star(color=YELLOW, fill_opacity=1).scale(0.4)
            
            car.move_to(LEFT * 4 + DOWN * 1)
            destination.move_to(RIGHT * 4 + UP * 1)
            
            self.play(FadeIn(car), FadeIn(destination))
            
            question = Text("How to find the shortest path?", font_size=32)
            question.next_to(title, DOWN, buff=0.5)
            self.play(Write(question))
        
        self.play(FadeOut(car), FadeOut(destination), FadeOut(question))
        
        with self.voiceover(text="Think of a map as a network of cities connected by roads, each with a distance. Dijkstra's Algorithm starts at your location and explores outward like ripples in a pond.") as tracker:
            vertices = {
                "A": LEFT * 4 + UP * 1,
                "B": LEFT * 2 + UP * 2,
                "C": LEFT * 2 + DOWN * 1,
                "D": RIGHT * 0 + UP * 1.5,
                "E": RIGHT * 0 + DOWN * 1.5,
                "F": RIGHT * 2.5 + UP * 0.5,
                "G": RIGHT * 4 + DOWN * 0.5
            }
            
            edges = [
                ("A", "B", 4),
                ("A", "C", 2),
                ("B", "D", 5),
                ("C", "B", 1),
                ("C", "E", 10),
                ("D", "F", 2),
                ("E", "D", 3),
                ("E", "F", 8),
                ("F", "G", 1),
                ("E", "G", 6)
            ]
            
            vertex_objects = {}
            vertex_labels = {}
            
            for name, pos in vertices.items():
                circle = Circle(radius=0.35, color=WHITE, fill_opacity=0.3, stroke_width=3)
                circle.move_to(pos)
                label = Text(name, font_size=28)
                label.move_to(pos)
                vertex_objects[name] = circle
                vertex_labels[name] = label
            
            edge_objects = {}
            edge_labels = {}
            
            for start, end, weight in edges:
                line = Line(vertices[start], vertices[end], color=GRAY, stroke_width=2)
                line.set_z_index(-1)
                edge_objects[(start, end)] = line
                
                midpoint = (vertices[start] + vertices[end]) / 2
                weight_label = Text(str(weight), font_size=20, color=GRAY)
                weight_label.move_to(midpoint)
                weight_label.shift(UP * 0.2 + RIGHT * 0.1)
                edge_labels[(start, end)] = weight_label
            
            self.play(
                *[Create(edge) for edge in edge_objects.values()],
                *[Write(label) for label in edge_labels.values()],
            )
            
            self.play(
                *[Create(circle) for circle in vertex_objects.values()],
                *[Write(label) for label in vertex_labels.values()],
            )
            
            vertex_objects["A"].set_fill(GREEN, opacity=0.7)
            self.play(vertex_objects["A"].animate.set_fill(GREEN, opacity=0.7))
            
            ripple1 = Circle(radius=0.35, color=BLUE).move_to(vertices["A"])
            ripple2 = Circle(radius=0.35, color=BLUE).move_to(vertices["A"])
            ripple3 = Circle(radius=0.35, color=BLUE).move_to(vertices["A"])
            
            self.play(
                ripple1.animate.scale(3).set_opacity(0),
                ripple2.animate.scale(5).set_opacity(0),
                ripple3.animate.scale(7).set_opacity(0),
                run_time=2
            )
        
        with self.voiceover(text="It visits the nearest unvisited city first, calculating the shortest path to get there. Watch as it marks each city with its distance from the start.") as tracker:
            distance_labels = {}
            
            distance_labels["A"] = Text("0", font_size=20, color=YELLOW)
            distance_labels["A"].next_to(vertex_objects["A"], DOWN, buff=0.3)
            self.play(Write(distance_labels["A"]))
            
            self.play(
                edge_objects[("A", "C")].animate.set_color(BLUE).set_stroke_width(4),
                vertex_objects["C"].animate.set_fill(BLUE, opacity=0.5)
            )
            distance_labels["C"] = Text("2", font_size=20, color=YELLOW)
            distance_labels["C"].next_to(vertex_objects["C"], DOWN, buff=0.3)
            self.play(Write(distance_labels["C"]))
            
            self.play(
                edge_objects[("A", "B")].animate.set_color(BLUE).set_stroke_width(4),
                vertex_objects["B"].animate.set_fill(BLUE, opacity=0.5)
            )
            distance_labels["B"] = Text("4", font_size=20, color=YELLOW)
            distance_labels["B"].next_to(vertex_objects["B"], UP, buff=0.3)
            self.play(Write(distance_labels["B"]))
        
        with self.voiceover(text="Here's the clever part: once it finds the shortest path to a city, it never revisits it. Instead, it uses that information to update distances to neighboring cities, always choosing the next closest one.") as tracker:
            vertex_objects["C"].set_fill(GREEN, opacity=0.7)
            self.play(vertex_objects["C"].animate.set_fill(GREEN, opacity=0.7))
            
            checkmark = Text("✓", font_size=32, color=GREEN)
            checkmark.move_to(vertex_objects["C"])
            self.play(FadeIn(checkmark, scale=1.5))
            self.play(FadeOut(checkmark))
            
            self.play(
                edge_objects[("C", "B")].animate.set_color(BLUE).set_stroke_width(4),
                vertex_objects["B"].animate.set_fill(ORANGE, opacity=0.5)
            )
            
            old_dist_B = distance_labels["B"]
            new_dist_B = Text("3", font_size=20, color=YELLOW)
            new_dist_B.next_to(vertex_objects["B"], UP, buff=0.3)
            self.play(Transform(old_dist_B, new_dist_B))
            
            self.play(
                edge_objects[("C", "E")].animate.set_color(BLUE).set_stroke_width(4),
                vertex_objects["E"].animate.set_fill(BLUE, opacity=0.5)
            )
            distance_labels["E"] = Text("12", font_size=20, color=YELLOW)
            distance_labels["E"].next_to(vertex_objects["E"], DOWN, buff=0.3)
            self.play(Write(distance_labels["E"]))
        
        with self.voiceover(text="The algorithm repeats this process, spreading outward until it reaches your destination.") as tracker:
            vertex_objects["B"].set_fill(GREEN, opacity=0.7)
            self.play(vertex_objects["B"].animate.set_fill(GREEN, opacity=0.7))
            
            self.play(
                edge_objects[("B", "D")].animate.set_color(BLUE).set_stroke_width(4),
                vertex_objects["D"].animate.set_fill(BLUE, opacity=0.5)
            )
            distance_labels["D"] = Text("8", font_size=20, color=YELLOW)
            distance_labels["D"].next_to(vertex_objects["D"], UP, buff=0.3)
            self.play(Write(distance_labels["D"]))
            
            vertex_objects["D"].set_fill(GREEN, opacity=0.7)
            self.play(vertex_objects["D"].animate.set_fill(GREEN, opacity=0.7))
            
            self.play(
                edge_objects[("D", "F")].animate.set_color(BLUE).set_stroke_width(4),
                vertex_objects["F"].animate.set_fill(BLUE, opacity=0.5)
            )
            distance_labels["F"] = Text("10", font_size=20, color=YELLOW)
            distance_labels["F"].next_to(vertex_objects["F"], UP, buff=0.3)
            self.play(Write(distance_labels["F"]))
            
            vertex_objects["F"].set_fill(GREEN, opacity=0.7)
            self.play(vertex_objects["F"].animate.set_fill(GREEN, opacity=0.7))
            
            self.play(
                edge_objects[("F", "G")].animate.set_color(BLUE).set_stroke_width(4),
                vertex_objects["G"].animate.set_fill(BLUE, opacity=0.5)
            )
            distance_labels["G"] = Text("11", font_size=20, color=YELLOW)
            distance_labels["G"].next_to(vertex_objects["G"], DOWN, buff=0.3)
            self.play(Write(distance_labels["G"]))
            
            vertex_objects["G"].set_fill(GOLD, opacity=1)
            self.play(
                vertex_objects["G"].animate.set_fill(GOLD, opacity=1).scale(1.2),
                Flash(vertex_objects["G"], color=YELLOW)
            )
        
        with self.voiceover(text="The result? The absolute shortest path guaranteed.") as tracker:
            path_edges = [("A", "C"), ("C", "B"), ("B", "D"), ("D", "F"), ("F", "G")]
            
            for edge in path_edges:
                self.play(
                    edge_objects[edge].animate.set_color(YELLOW).set_stroke_width(8),
                    run_time=0.4
                )
            
            path_text = Text("Shortest Path: A → C → B → D → F → G", font_size=28, color=YELLOW)
            path_text.to_edge(DOWN, buff=0.5)
            self.play(Write(path_text))
            
            total_distance = Text("Total Distance: 11", font_size=32, color=GREEN)
            total_distance.next_to(path_text, UP, buff=0.3)
            self.play(Write(total_distance))
        
        self.play(
            FadeOut(VGroup(*[obj for obj in vertex_objects.values()])),
            FadeOut(VGroup(*[obj for obj in vertex_labels.values()])),
            FadeOut(VGroup(*[obj for obj in edge_objects.values()])),
            FadeOut(VGroup(*[obj for obj in edge_labels.values()])),
            FadeOut(VGroup(*[obj for obj in distance_labels.values()])),
            FadeOut(path_text),
            FadeOut(total_distance)
        )
        
        with self.voiceover(text="This elegant approach powers navigation apps, network routing, and even video game AI. Dijkstra's Algorithm proves that sometimes the smartest way forward is simply taking one optimal step at a time.") as tracker:
            applications = VGroup(
                Text("📱 Navigation Apps", font_size=36),
                Text("🌐 Network Routing", font_size=36),
                Text("🎮 Video Game AI", font_size=36)
            ).arrange(DOWN, buff=0.8)
            
            for app in applications:
                self.play(FadeIn(app, shift=UP))
                self.wait(0.3)
            
            self.wait(0.5)
            
            self.play(FadeOut(applications))
            
            final_message = Text("One optimal step at a time", font_size=48, gradient=(BLUE, GREEN))
            self.play(Write(final_message))
            self.wait(0.5)
            
            self.play(FadeOut(final_message), FadeOut(title))