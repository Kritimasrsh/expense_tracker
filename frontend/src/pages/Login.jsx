import { useState } from "react";
import api from "../api/axios";
import { useNavigate, Link } from "react-router-dom";

import Button from "../components/Button";
import Input from "../components/Input";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState("password");
  const [pendingEmail, setPendingEmail] = useState("");
  const [message, setMessage] = useState("");

  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleLogin = async () => {
    if (!email || !password) {
      setError("Fill all fields"); 
      return;
    }

    try {
      setLoading(true);
      setError(""); 

      const res = await api.post("/auth/login", {
        email,
        password,
      });

      setPendingEmail(email);
      setStep("otp");
      setMessage(res.data.message || "OTP sent to your email."); // success message

      if (res.data.debug_otp) {
        console.log("Development OTP received"); 
      }

    } catch (err) {
      setError(err.response?.data?.detail || "Invalid credentials"); // backend error shown in UI
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    if (!otp || !pendingEmail) {
      setError("Enter the OTP"); 
      return;
    }

    try {
      setLoading(true);
      setError(""); // clear errors

      const res = await api.post("/auth/verify-otp", {
        email: pendingEmail,
        otp_code: otp,
      });

      localStorage.setItem("token", res.data.access_token);

      navigate("/dashboard"); 

    } catch (err) {
      setError(err.response?.data?.detail || "Invalid OTP"); 
    } finally {
      setLoading(false);
    }
  };

  const resetLogin = () => {
    setStep("password");
    setOtp("");
    setMessage("");
    setPendingEmail("");
    setError(""); 
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 px-4">

      <div className="w-full max-w-5xl bg-white rounded-3xl overflow-hidden shadow-2xl grid md:grid-cols-2">

        {/* LEFT SIDE UI */}
        <div className="hidden md:flex flex-col justify-center bg-gradient-to-br from-sky-500 to-blue-600 text-white p-14">

          <h1 className="text-5xl font-bold leading-tight">
            Expense Tracker
          </h1>

          <p className="mt-6 text-sky-100 text-lg leading-relaxed">
            Manage your expenses, visualize your spending,
            and gain complete control over your finances.
          </p>

        </div>

        {/* RIGHT SIDE UI */}
        <div className="p-10 md:p-14 flex flex-col justify-center">

          <h2 className="text-3xl font-bold text-slate-800">
            Welcome Back
          </h2>

          <p className="text-slate-500 mt-2 mb-4">
            Login to continue
          </p>

          {/* NEW: ERROR DISPLAY UI */}
          {error && (
            <div className="bg-red-100 text-red-600 p-3 rounded-lg text-sm mb-4">
              {error}
            </div>
          )}

          <div className="space-y-5">

            {step === "password" ? (
              <>
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

                <Button loading={loading} onClick={handleLogin}>
                  Login
                </Button>
              </>
            ) : (
              <>
                {/* OTP INFO BOX */}
                <div className="rounded-xl bg-slate-100 p-4 text-sm text-slate-700">
                  {message || `Enter the 6-digit code sent to ${pendingEmail}.`}
                </div>

                <Input
                  placeholder="Enter OTP"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                />

                <Button loading={loading} onClick={handleVerifyOtp}>
                  Verify OTP
                </Button>

                <button
                  type="button"
                  onClick={resetLogin}
                  className="text-sm text-slate-500 underline"
                >
                  Back to login
                </button>
              </>
            )}

          </div>

          {step === "password" ? (
            <p className="text-sm text-center text-slate-500 mt-8">
              Don’t have an account?{" "}
              <Link to="/signup" className="text-sky-500 font-semibold">
                Sign Up
              </Link>
            </p>
          ) : null}

        </div>

      </div>

    </div>
  );
}