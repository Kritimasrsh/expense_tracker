import { Link } from "react-router-dom";

export default function DashboardLayout({ children }) {
  return (
    <div className="min-h-screen bg-slate-100 flex">

      {/* SIDEBAR */}
      <div className="hidden md:flex w-64 bg-white border-r border-slate-200 flex-col p-6">

        <h1 className="text-2xl font-bold text-sky-500">
          Expense Tracker
        </h1>

        <div className="mt-10 space-y-3">

          <Link
            to="/dashboard"
            className="block bg-sky-50 text-sky-600 px-4 py-3 rounded-xl font-medium"
          >
            📊 Dashboard
          </Link>

          <button
            className="w-full text-left text-slate-600 hover:bg-slate-100 px-4 py-3 rounded-xl transition"
          >
            💰 Expenses
          </button>

          <button
            className="w-full text-left text-slate-600 hover:bg-slate-100 px-4 py-3 rounded-xl transition"
          >
            📈 Analytics
          </button>

          <button
            className="w-full text-left text-slate-600 hover:bg-slate-100 px-4 py-3 rounded-xl transition"
          >
            ⚙ Settings
          </button>

        </div>

      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 p-6">
        {children}
      </div>

    </div>
  );
}