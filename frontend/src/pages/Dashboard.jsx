import { useEffect, useState } from "react";
import api from "../api/axios";
import { useNavigate } from "react-router-dom";



import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from "recharts";

export default function Dashboard() {
  const [expenses, setExpenses] = useState([]);
  const [title, setTitle] = useState("");
  const [amount, setAmount] = useState("");


  // PROFILE STATES (ADDED)
  const [user, setUser] = useState(null);
  const [file, setFile] = useState(null);

  const [preview, setPreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const navigate = useNavigate();

  const loadExpenses = async () => {
    try {
      const res = await api.get("/expense/");
      setExpenses(res.data);
    } catch (error) {
      console.error("Failed to load expenses", error);
      if (error.response?.status === 401) {
        localStorage.removeItem("token");
        navigate("/");
      }
    }
  };

  // PROFILE LOAD (ADDED)
   const loadUser = async () => {
    try {
    const res = await api.get("/user/me");
    setUser(res.data);
   } catch (err) {
    console.log("Failed to load user", err);
    }
  };

  useEffect(() => {
   const token = localStorage.getItem("token");
    if (!token) {
      navigate("/");
      return;
   }

   loadExpenses();
   loadUser(); 
  }, [navigate]);

  const addExpense = async () => {
    if (!title || !amount) return;

    try {
      await api.post("/expense/", {
        title,
        amount: Number(amount),
      });

      setTitle("");
      setAmount("");
      loadExpenses();
    } catch (error) {
      console.error("Add expense failed", error);
      alert("Failed to add expense");
    }
  };

  const deleteExpense = async (id) => {
    try {
      await api.delete(`/expense/${id}`);
      loadExpenses();
    } catch (error) {
      console.error("Delete expense failed", error);
      alert("Failed to delete expense");
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  const total = expenses.reduce((sum, e) => sum + e.amount, 0);
  const average = expenses.length ? total / expenses.length : 0;

  const generateColor = (index) => {
    const hue = (index * 47) % 360;
    return `hsl(${hue}, 70%, 55%)`;
  };

  const months = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
  ];

  const monthlyData = months.map((m) => {
    const monthIndex = months.indexOf(m) + 1;

    const total = expenses
      .filter((e) => {
        const date = new Date(e.created_at || Date.now());
        return date.getMonth() + 1 === monthIndex;
      })
      .reduce((sum, e) => sum + e.amount, 0);

    return {
      month: m,
      expense: total,
    };
  });

  // PROFILE HANDLERS (ADDED)
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
  };

  const uploadProfile = async () => {
    if (!selectedFile) return;

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      await api.post("/user/upload-profile-picture", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setSelectedFile(null);
      loadUser();
    } catch (err) {
      alert("Failed to upload profile picture");
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 p-6">

      {/* HEADER */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">
            Expense Dashboard
          </h1>
          <p className="text-slate-500">
            Track spending with insights
          </p>
        </div>

        {/* PROFILE UI (ADDED ONLY - NO CHANGE TO EXISTING CODE) */}
        <div className="flex items-center gap-4 bg-white px-4 py-2 rounded-xl shadow-sm">

          <div className="w-12 h-12 rounded-full overflow-hidden border">
            <img
              src={
                preview
                  ? preview
                  : user?.profile_picture
                  ? `http://localhost:8000${user.profile_picture}`
                  : "https://via.placeholder.com/100"
              }
              className="w-full h-full object-cover"
            />
          </div>

          <div>
            <p className="font-semibold">{user?.name || "User"}</p>
            <p className="text-xs text-slate-500">{user?.email}</p>

            <input
              type="file"
              onChange={handleFileChange}
              className="text-xs mt-1"
            />

            {selectedFile && (
              <button
                onClick={uploadProfile}
                className="text-xs bg-sky-500 text-white px-2 py-1 rounded mt-1"
              >
                Save
              </button>
            )}
          </div>

        </div>

        <button
          onClick={logout}
          className="bg-red-500 hover:bg-red-600 text-white px-5 py-2 rounded-xl"
        >
          Logout
        </button>
      </div>

      {/* STATS */}
      <div className="grid md:grid-cols-3 gap-4 mb-6">

        <div className="bg-white p-5 rounded-2xl shadow-sm">
          <p className="text-slate-500">Total Expense</p>
          <h2 className="text-3xl font-bold text-emerald-500">
            Rs {total}
          </h2>
        </div>

        <div className="bg-white p-5 rounded-2xl shadow-sm">
          <p className="text-slate-500">Total Items</p>
          <h2 className="text-3xl font-bold text-sky-500">
            {expenses.length}
          </h2>
        </div>

        <div className="bg-white p-5 rounded-2xl shadow-sm">
          <p className="text-slate-500">Average Expense</p>
          <h2 className="text-3xl font-bold text-indigo-500">
            Rs {average.toFixed(2)}
          </h2>
        </div>

      </div>

      {/* MAIN DASHBOARD */}
      <div className="flex flex-col lg:flex-row gap-6 min-h-[75vh]">

        {/* LEFT SIDE */}
        <div className="w-full lg:w-1/3 flex flex-col gap-6">

          {/* ADD */}
          <div className="bg-white p-5 rounded-2xl shadow-sm">
            <h2 className="font-semibold mb-4">Add Expense</h2>

            <input
              className="w-full border p-3 rounded-xl mb-3"
              placeholder="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />

            <input
              className="w-full border p-3 rounded-xl mb-3"
              placeholder="Amount"
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />

            <button
              onClick={addExpense}
              className="w-full bg-sky-500 hover:bg-sky-600 text-white py-3 rounded-xl"
            >
              Add Expense
            </button>
          </div>

          {/* EXPENSE LIST */}
          <div className="bg-white p-5 rounded-2xl shadow-sm flex-1 flex flex-col">
            <h2 className="font-semibold mb-4">Expenses</h2>

            <div className="space-y-3 overflow-auto flex-1 pr-1">

              {expenses.map((e) => (
                <div
                  key={e.id}
                  className="flex justify-between items-center border border-gray-300 p-3 rounded-xl bg-slate-50 hover:bg-slate-100 transition"
                >
                  <div>
                    <p className="font-medium">{e.title}</p>
                    <p className="text-sm text-slate-500">
                      Rs {e.amount}
                    </p>
                  </div>

                  <button
                    onClick={() => deleteExpense(e.id)}
                    className="text-xs px-3 py-1 rounded-lg bg-green-200 text-green-800 hover:bg-green-300"
                  >
                    Delete
                  </button>
                </div>
              ))}

            </div>
          </div>

        </div>

        {/* RIGHT SIDE */}
        <div className="w-full lg:w-2/3 flex flex-col gap-6">

          {/* PIE CHART */}
          <div className="bg-white p-5 rounded-2xl shadow-sm flex-1">
            <h2 className="font-semibold mb-4">Expense Breakdown</h2>

            <div className="h-[300px]">
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={expenses}
                    dataKey="amount"
                    nameKey="title"
                    outerRadius={120}
                    label
                  >
                    {expenses.map((_, i) => (
                      <Cell key={i} fill={generateColor(i)} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* MONTHLY */}
          <div className="bg-white p-5 rounded-2xl shadow-sm flex-1">
            <h2 className="font-semibold mb-4">
              Monthly Expenses (Jan - Dec)
            </h2>

            <div className="h-[300px]">
              <ResponsiveContainer>
                <BarChart data={monthlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="expense" fill="#0ea5e9" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}