import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const MCP_SERVER_URL = 'http://localhost:8000/mcp'; // Update if needed

function BookingCard({ booking, onCancel, onReschedule }) {
  return (
    <div className="booking-card">
      <div><strong>Reference:</strong> {booking.reference}</div>
      <div><strong>Status:</strong> <span className={booking.status.toLowerCase()}>{booking.status}</span></div>
      <div><strong>Details:</strong> {booking.details}</div>
      <div className="actions">
        <button onClick={() => onCancel(booking.reference)} disabled={booking.status === 'CANCELLED'}>Cancel</button>
        <button onClick={() => onReschedule(booking.reference)} disabled={booking.status !== 'CONFIRMED'}>Reschedule</button>
      </div>
    </div>
  );
}

function ChatMessage({ sender, text }) {
  return (
    <div className={`chat-message ${sender}`}> <b>{sender === 'user' ? 'You' : 'Assistant'}:</b> {text} </div>
  );
}

function App() {
  const [chatHistory, setChatHistory] = useState(() => JSON.parse(localStorage.getItem('chatHistory')) || []);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [bookings, setBookings] = useState([]);
  const chatEndRef = useRef(null);

  useEffect(() => {
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { sender: 'user', text: input };
    setChatHistory(prev => [...prev, userMsg]);
    setLoading(true);
    setInput('');
    try {
      const res = await axios.post(MCP_SERVER_URL, { message: input });
      const assistantMsg = { sender: 'assistant', text: res.data.response };
      setChatHistory(prev => [...prev, assistantMsg]);
      if (res.data.bookings) setBookings(res.data.bookings);
    } catch (err) {
      setChatHistory(prev => [...prev, { sender: 'assistant', text: 'Error: Could not reach server.' }]);
    }
    setLoading(false);
  };

  const handleCancel = async (reference) => {
    setLoading(true);
    try {
      const res = await axios.post(MCP_SERVER_URL, { action: 'cancel', reference });
      setChatHistory(prev => [...prev, { sender: 'assistant', text: res.data.response }]);
      if (res.data.bookings) setBookings(res.data.bookings);
    } catch {
      setChatHistory(prev => [...prev, { sender: 'assistant', text: 'Error: Could not cancel booking.' }]);
    }
    setLoading(false);
  };

  const handleReschedule = async (reference) => {
    setLoading(true);
    try {
      const res = await axios.post(MCP_SERVER_URL, { action: 'reschedule', reference });
      setChatHistory(prev => [...prev, { sender: 'assistant', text: res.data.response }]);
      if (res.data.bookings) setBookings(res.data.bookings);
    } catch {
      setChatHistory(prev => [...prev, { sender: 'assistant', text: 'Error: Could not reschedule booking.' }]);
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <h1>Flight Reservation Assistant</h1>
      <div className="chat-stream">
        {chatHistory.map((msg, idx) => <ChatMessage key={idx} sender={msg.sender} text={msg.text} />)}
        {loading && <div className="loading-spinner">Assistant is typing...</div>}
        <div ref={chatEndRef} />
      </div>
      <div className="input-row">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type your message..."
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>Send</button>
      </div>
      <div className="bookings-section">
        {bookings.length > 0 && <h2>Your Bookings</h2>}
        {bookings.map(b => (
          <BookingCard
            key={b.reference}
            booking={b}
            onCancel={handleCancel}
            onReschedule={handleReschedule}
          />
        ))}
      </div>
    </div>
  );
}

export default App;
