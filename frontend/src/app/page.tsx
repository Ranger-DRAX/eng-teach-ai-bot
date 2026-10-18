import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 text-center">
      <div className="max-w-md w-full p-8 bg-white rounded-3xl shadow-sm border border-slate-100">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">
          🌟
        </div>
        <h1 className="text-2xl font-bold text-slate-800 mb-2">
          English Learning Chatbot
        </h1>
        <p className="text-slate-600 mb-6 text-sm">
          A gentle, encouraging English learning companion for children under 7.
        </p>
        <div className="flex flex-col gap-3">
          <Link
            href="/chat"
            className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition duration-150"
          >
            Start Learning 🚀
          </Link>
          <Link
            href="/dashboard"
            className="w-full py-3 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-xl transition duration-150"
          >
            Parent Dashboard 📊
          </Link>
        </div>
      </div>
    </main>
  );
}
