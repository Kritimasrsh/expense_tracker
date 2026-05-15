export default function Input(props) {
  return (
    <input
      {...props}
      className="w-full p-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-400"
    />
  );
}