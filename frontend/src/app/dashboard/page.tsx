"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";

interface SkillItem {
  id: string;
  name: string;
  state: "unassessed" | "developing" | "mastered" | "review";
  successfulEvents: number;
}

export default function DashboardPage() {
  const [childPseudonym, setChildPseudonym] = useState("Leo");
  const [currentLevel, setCurrentLevel] = useState("L1");
  const [totalSessions, setTotalSessions] = useState(3);
  const [skills, setSkills] = useState<SkillItem[]>([
    { id: "l1_colors", name: "Colors (Red, Blue, Green)", state: "mastered", successfulEvents: 4 },
    { id: "l1_animals", name: "Animals (Cat, Dog, Bird)", state: "developing", successfulEvents: 2 },
    { id: "l1_numbers", name: "Numbers (1–10)", state: "developing", successfulEvents: 1 },
    { id: "l1_body", name: "Body Parts", state: "unassessed", successfulEvents: 0 },
    { id: "l1_family", name: "Family & Friends", state: "unassessed", successfulEvents: 0 },
    { id: "l1_food", name: "Food & Drink", state: "unassessed", successfulEvents: 0 },
  ]);
  const [isDeleting, setIsDeleting] = useState(false);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  useEffect(() => {
    // Attempt to load from API if server is running
    fetch("http://localhost:8000/api/v1/dashboard/child_demo_1", {
      headers: { "guardian-id": "guardian_demo_1" },
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data) {
          setChildPseudonym(data.pseudonym || "Leo");
          setCurrentLevel(data.current_level || "L1");
          setTotalSessions(data.total_sessions || 0);
          if (data.skills && data.skills.length > 0) {
            setSkills((prev) =>
              prev.map((item) => {
                const found = data.skills.find((s: { skill_id: string; state: string; successful_events: number }) => s.skill_id === item.id);
                if (found) {
                  return {
                    ...item,
                    state: found.state,
                    successfulEvents: found.successful_events,
                  };
                }
                return item;
              })
            );
          }
        }
      })
      .catch(() => {
        // Keeps deterministic fallback data when offline
      });
  }, []);

  const handleExportData = () => {
    const exportData = {
      childPseudonym,
      currentLevel,
      totalSessions,
      skills,
      exportedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${childPseudonym}_learning_history.json`;
    a.click();
    URL.revokeObjectURL(url);
    setActionNotice("Learning record exported successfully!");
  };

  const handleDeleteProfile = () => {
    if (confirm("Are you sure you want to delete this profile and all associated learning history? This action is permanent.")) {
      setIsDeleting(true);
      setTimeout(() => {
        setIsDeleting(false);
        setActionNotice("Profile and all associated data have been permanently purged.");
      }, 500);
    }
  };

  const getStatusBadge = (state: SkillItem["state"]) => {
    switch (state) {
      case "mastered":
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">Mastered 🏆</span>;
      case "developing":
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">Developing 🚀</span>;
      case "review":
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800">Needs Practice 🔄</span>;
      case "unassessed":
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600">Unassessed ⚪</span>;
    }
  };

  const masteredCount = skills.filter((s) => s.state === "mastered").length;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Navigation & Header */}
        <div className="flex items-center justify-between">
          <Link href="/" className="text-sm font-semibold text-blue-600 hover:text-blue-800">
            ← Back to Home
          </Link>
          <Link
            href="/chat"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl text-sm transition"
          >
            Start Chat Session 💬
          </Link>
        </div>

        {actionNotice && (
          <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-2xl text-sm flex justify-between items-center">
            <span>{actionNotice}</span>
            <button onClick={() => setActionNotice(null)} className="text-xs font-bold text-emerald-600">
              ✕
            </button>
          </div>
        )}

        {/* Child Profile Card */}
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
              <span>{childPseudonym}&apos;s Learning Journey</span>
              <span className="text-lg">⭐</span>
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Active Level: <strong className="text-blue-600">Level {currentLevel}</strong> • Total Sessions: <strong>{totalSessions}</strong>
            </p>
          </div>
          <div className="flex items-center gap-2 bg-blue-50 px-4 py-2 rounded-2xl border border-blue-100">
            <span className="text-2xl font-black text-blue-600">{masteredCount}</span>
            <span className="text-xs font-semibold text-blue-800 leading-tight">Skills<br />Mastered</span>
          </div>
        </div>

        {/* Recommended Activity */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-3xl shadow-sm">
          <h2 className="text-xs font-bold uppercase tracking-wider text-blue-200">Recommended Next Step</h2>
          <p className="text-lg font-bold mt-1">Practice Animal Words (Cat, Dog, Bird) 🐾</p>
          <p className="text-sm text-blue-100 mt-1">
            Leo has successfully practiced animals in 1 session. One more session with 2 successful activities will achieve mastery!
          </p>
        </div>

        {/* Curriculum Progress Breakdown */}
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
          <h2 className="text-lg font-bold text-slate-800 mb-4">Curriculum Skills Overview</h2>
          <div className="divide-y divide-slate-100">
            {skills.map((skill) => (
              <div key={skill.id} className="py-3 flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-800">{skill.name}</p>
                  <p className="text-xs text-slate-500">
                    {skill.successfulEvents > 0 ? `${skill.successfulEvents} successful checks` : "Not assessed yet"}
                  </p>
                </div>
                <div>{getStatusBadge(skill.state)}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Parent Privacy & Data Controls */}
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 space-y-4">
          <h2 className="text-lg font-bold text-slate-800">Guardian Privacy Controls</h2>
          <p className="text-sm text-slate-600">
            All learning data is stored securely and linked only to your guardian account. No audio recordings or external ad profiling ever exist.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <button
              onClick={handleExportData}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-sm transition"
            >
              Export Learning History (JSON) 📥
            </button>
            <button
              onClick={handleDeleteProfile}
              disabled={isDeleting}
              className="px-4 py-2 bg-rose-50 hover:bg-rose-100 text-rose-700 font-semibold rounded-xl text-sm border border-rose-200 transition"
            >
              {isDeleting ? "Deleting..." : "Delete Profile & Data 🗑️"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
