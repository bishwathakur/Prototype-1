import React, { useState, useEffect } from 'react';

function App() {
  const [itinerary, setItinerary] = useState(null);

  useEffect(() => {
    const fetchItinerary = async () => {
      try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${API_URL}/api/itinerary/CM-123`);
        if (response.ok) {
          const data = await response.json();
          setItinerary(data);
        }
      } catch (error) {
        console.error('Error fetching itinerary:', error);
      }
    };

    fetchItinerary();
    const interval = setInterval(fetchItinerary, 2000);
    return () => clearInterval(interval);
  }, []);

  let cardColor = 'bg-gray-100 border-gray-500 text-gray-800';
  let message = 'Loading...';

  if (itinerary) {
    if (itinerary.status === 'ON_TIME') {
      cardColor = 'bg-green-100 border-green-500 text-green-800';
      message = 'Flight ' + itinerary.original_flight + ' is On Time.';
    } else if (itinerary.status === 'CANCELLED') {
      cardColor = 'bg-red-100 border-red-500 text-red-800';
      message = 'Flight ' + itinerary.original_flight + ' Cancelled. AXIS is currently finding alternatives...';
    } else if (itinerary.status === 'REBOOKED') {
      cardColor = 'bg-yellow-100 border-yellow-500 text-yellow-800';
      message = 'AXIS resolved your disruption. You are rebooked on ' + itinerary.new_flight + '. No action required.';
    } else if (itinerary.status === 'INELIGIBLE') {
      cardColor = 'bg-gray-100 border-gray-500 text-gray-800';
      message = 'Flight ' + itinerary.original_flight + ' Cancelled — not eligible for auto-rebooking.';
      if (itinerary.ineligible_reason) {
        message += ' Reason: ' + itinerary.ineligible_reason;
      }
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-8 font-sans">
      <h1 className="text-3xl font-bold text-blue-900 mb-8">American Express AXIS Concierge</h1>

      <div className={"w-full max-w-lg p-6 border-l-4 rounded shadow-md transition-colors duration-500 " + cardColor}>
        <p className="text-lg font-medium">{message}</p>
      </div>
    </div>
  );
}

export default App;