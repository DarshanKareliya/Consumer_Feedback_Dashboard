import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
  // State to hold the current input value
  const [query, setQuery] = useState('');

  // Handler for updating state as the user types
  const handleInputChange = (event) => {
    setQuery(event.target.value);
  };

  // Handler for form submission to trigger the search
  const handleSubmit = (event) => {
    event.preventDefault(); // Prevents the default page reload
    if (query.trim()) {
      onSearch(query.trim()); // Passes the cleaned query to the parent component
    }
  };

  // Handler to clear the search input
  const handleClear = () => {
    setQuery('');
    onSearch(''); // Triggers search with an empty string to reset results
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '8px', width: '100%', maxWidth: '500px' }}>
      <div style={{ position: 'relative', flex: 1, display: 'flex', alignItems: 'center' }}>
        <input
          type="text"
          value={query}
          onChange={handleInputChange}
          placeholder="Search comments..."
          style={{
            width: '100%',
            padding: '8px 32px 8px 12px',
            borderRadius: '4px',
            border: '1px solid #ccc',
            fontSize: '1rem'
          }}
        />
        {/* Render clear button only if there is text */}
        {query && (
          <button
            type="button"
            onClick={handleClear}
            style={{
              position: 'absolute',
              right: '8px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '1.2rem',
              color: '#888'
            }}
            aria-label="Clear search"
          >
            &times;
          </button>
        )}
      </div>
      
      <button 
        type="submit"
        style={{
          padding: '8px 16px',
          backgroundColor: '#0d6efd',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '1rem'
        }}
      >
        Search
      </button>
    </form>
  );
};

export default SearchBar;