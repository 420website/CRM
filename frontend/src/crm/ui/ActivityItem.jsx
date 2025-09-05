import React from "react";
import { useNavigate } from "react-router-dom";

// Item is a regesitraion item.
export default function ActivityItem({ item }) {
  const navigate = useNavigate();

  const status =
    new Date(`${item.date}T${item.time}`) > new Date()
      ? "upcoming"
      : "completed";

  return (
    <div
      key={item.id}
      className="border rounded-lg p-4 bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer"
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {item.description}
            </h3>
            <span
              className={`px-2 py-1 text-xs font-medium rounded-full ${
                status === "upcoming"
                  ? "bg-blue-100 text-blue-800"
                  : "bg-green-100 text-green-800"
              }`}
            >
              {status === "upcoming" ? "Upcoming" : "Completed"}
            </span>
          </div>
          <div className="text-sm text-gray-600 mt-1">
            <p className="font-medium">
              Client: {item.first_name} {item.last_name}
              {item.disposition && (
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-md text-xs font-normal ml-2">
                  {item.disposition.charAt(0).toUpperCase() +
                    item.disposition.slice(1).toLowerCase()}
                </span>
              )}
            </p>
            <p>Date: {item.date}</p>
            {item.time && <p>Time: {item.time}</p>}
            {item.phone1 && <p>Phone: {item.phone1}</p>}
            <p className="text-xs text-gray-500 mt-1">Activity ID: {item.id}</p>
          </div>
        </div>
      </div>

      <div className="flex gap-2 mt-4">
        <button
          onClick={() => {
            navigate(`/admin-edit/${item.patient_id}`);
          }}
          className="bg-black hover:bg-gray-800 text-white py-2 px-4 rounded-md transition-colors text-xs font-medium"
        >
          View Client Profile
        </button>
      </div>
    </div>
  );
}
