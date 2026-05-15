export default function Button({ children, loading, ...props }) {
  return (
    <button
      {...props}
      disabled={loading}
      className="w-full bg-sky-500 hover:bg-sky-600 text-white py-3 rounded-xl font-semibold transition"
    >
      {loading ? "Loading..." : children}
    </button>
  );
}