import { useState } from "react";
import api from "../api/axios";
import { useNavigate, Link } from "react-router-dom";
import Input from "../components/Input";
import Button from "../components/Button";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const signup = async () => {
    if (!email || !password) {
      alert("Fill all fields");
      return;
    }

    try {
      setLoading(true);

      const res = await api.post("/auth/signup", {
        email,
        password,
      });

      localStorage.setItem("token", res.data.access_token);
      navigate("/dashboard");
    } catch {
      alert("Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">

      <div className="w-full max-w-4xl bg-white rounded-3xl shadow-xl grid md:grid-cols-2">

        <div className="hidden md:flex items-center justify-center bg-sky-500 text-white p-10">
          <h1 className="text-4xl font-bold">Join Us</h1>
        </div>

        <div className="p-10 space-y-5">

          <h2 className="text-2xl font-bold">Signup</h2>

          <Input
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <Button onClick={signup} loading={loading}>
            Create Account
          </Button>

          <p className="text-sm">
            Already have account? <Link to="/" className="text-sky-500">Login</Link>
          </p>

        </div>
      </div>
    </div>
  );
}