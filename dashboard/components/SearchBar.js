"use client";
import "@fortawesome/fontawesome-free/css/all.min.css";

export default function SearchBar() {
  return (
    <div className="flex flex-col items-center">
      <div>
        <h1>Map Search Tool</h1>
      </div>
      <div className="relative m-2">
        <input
          type="text"
          placeholder="Search..."
          className="border border-gray-300 rounded pl-8 p-1"
        />
        <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
          <i className="fas fa-search"></i> {/* Font Awesome Search Icon */}
        </span>
      </div>
    </div>
  );
}
