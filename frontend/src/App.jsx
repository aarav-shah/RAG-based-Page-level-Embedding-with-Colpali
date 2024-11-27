import React, { useState, useEffect ,useRef} from 'react';
import './App.css';
import Loader from './Loader'
function formatText(text) {
  let formattedText = text
    // Bold: Convert **text** to <strong>text</strong>
    .replace(/Percentage Decrease/g, '<strong>Percentage Decrease</strong>')
    .replace(/Percentage Increase/g, '<strong>Percentage Increase</strong>')

    // Operators and Inline Math: Support parentheses and inline division
    .replace(/\((.*?) - (.*?) \/ (.*?)\)/g, '($1 - $2 / $3)')
    .replace(/\((.*?)\) × (.*?) /g, '($1) × $2')


    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

    // Italic: Convert _text_ to <em>text</em>
    .replace(/_(.*?)_/g, '<em>$1</em>')

    // Fractions: Convert \frac{a}{b} to HTML fraction format
    .replace(/\\frac{(.*?)}{(.*?)}/g, '<span>($1 / $2)</span>')

    // Square root: Convert \sqrt{value} to √(value)
    .replace(/\\sqrt{(.*?)}/g, '√($1)')

    // Exponents: Convert x^{n} to x^n
    .replace(/(\w)\^{(.*?)}/g, '$1^$2')

    // Grouping brackets \left and \right
    .replace(/\\left/g, '')
    .replace(/\\right/g, '')

    // Greek symbols, e.g., \alpha, \beta
    .replace(/\\alpha/g, 'α')
    .replace(/\\beta/g, 'β')
    .replace(/\\gamma/g, 'γ')
    .replace(/\\delta/g, 'δ')
    .replace(/\\epsilon/g, 'ε')
    .replace(/\\lambda/g, 'λ')
    .replace(/\\pi/g, 'π')
    .replace(/\\sigma/g, 'σ')
    .replace(/\\theta/g, 'θ')

    // Operations: Convert \times and \div
    .replace(/\\times/g, '×')
    .replace(/\\div/g, '÷')

    // Integrals: Convert \int_a^b to ∫(a, b)
    .replace(/\\int_{(.*?)}\^{(.*?)}/g, '∫($1, $2)')

    // Summation: Convert \sum_{i=1}^n to Σ (i=1 to n)
    .replace(/\\sum_{(.*?)}\^{(.*?)}/g, 'Σ ($1 to $2)')

    // Lim: Convert \lim_{x \to 0} to lim(x→0)
    .replace(/\\lim_{(.*?)\\to(.*?)}/g, 'lim($1→$2)')

    // Headings: Convert ### text to <h3>text</h3>
    .replace(/### (.*?)(?=\n|$)/g, '<h3>$1</h3>')

    // Bullet points: Convert "* text" to list items
    .replace(/(?:\r\n|\r|\n)\* (.*?)(?=\n|$)/g, '<li>$1</li>')

    // Paragraph breaks: Convert double newlines to paragraph breaks
    .replace(/(?:\r\n|\r|\n){2,}/g, '</p><p>')

    // Wrap any standalone list items with <ul> tags
    .replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>')

    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

    // Italic: Convert _text_ to <em>text</em>
    .replace(/_(.*?)_/g, '<em>$1</em>')

    // Fractions: Convert \frac{a}{b} to HTML fraction format
    .replace(/\\frac{(.*?)}{(.*?)}/g, '<span>($1 / $2)</span>')

    // Percentage Calculation: Convert expressions like \left( a - b / b \right) * 100
    .replace(/\\left\((.*?)\\right\)/g, '<span>($1)</span>')
    .replace(/\((.*?)\)/g, '($1)')

    // Multiplication symbol: Convert \times to multiplication symbol
    .replace(/\\times/g, '×')

    // Percentage symbol: Convert * 100 to * 100%
    .replace(/\* 100/g, '* 100%')

    // Handle generic \text{} formatting
    .replace(/\\text{(.*?)}/g, '$1')

    // Headings: Convert ### text to <h3>text</h3>
    .replace(/### (.*?)(?=\n|$)/g, '<h3>$1</h3>')

    // Bullet points: Convert "* text" to list items
    .replace(/(?:\r\n|\r|\n)\* (.*?)(?=\n|$)/g, '<li>$1</li>')

    // Paragraph breaks: Convert double newlines to paragraph breaks
    .replace(/(?:\r\n|\r|\n){2,}/g, '</p><p>')

    // Wrap any standalone list items with <ul> tags
    .replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>');

  // Wrap the formatted text in <p> tags
  formattedText = `<p>${formattedText}</p>`;

  return formattedText;
}

function App() {
  const [query, setQuery] = useState('');
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(false); // State to track loading
  const chatWindowRef = useRef(null); // Ref for chat window

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [chats, loading]);

  useEffect(() => {
    const storedChats = JSON.parse(localStorage.getItem('chats')) || [];
    setChats(storedChats);
  }, []);

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent any default action
        handleSubmit();
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const newChat = { Query: query };
    setQuery("")
    setLoading(true); // Start loader
    const updatedChats = [...chats, { query }];
    setChats(updatedChats);

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newChat),
      });

      const data = await response.json();
      const formattedResponse = formatText(data.answer);
      const updatedChats = [...chats, { query, response: formattedResponse }];

      setChats(updatedChats);
      localStorage.setItem('chats', JSON.stringify(updatedChats));
      setQuery('');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false); // Stop loader
    }
  };

  return (
    <div className="app-container">
      <h1 className="app-title">SAMHSA CHATBOT</h1>
      {chats.length >0 && <div className="chat-window" ref={chatWindowRef}>
        {chats.map((chat, index) => (
          <div
            key={index}
            className={`chat-message ${index % 2 === 0 ? 'chat-dark' : 'chat-light'}`}
          >
            <div className="user-text">{chat.query}</div>
            <div
              className="bot-text"
              dangerouslySetInnerHTML={{ __html: chat.response }}
            />
          </div>
        ))}
        {loading && <Loader />} {/* Show loader when loading */}
      </div>}
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"

          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type your query here..."
          className="chat-input"
        />
        <button type="submit" className="chat-button"></button>
      </form>
    </div>
  );
}

export default App;