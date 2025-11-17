/**
 * App Component
 * Root application component
 */

import React from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ChatPage } from './components/ChatPage';
import './styles/main.css';

function App() {
  return (
    <ErrorBoundary>
      <ChatPage />
    </ErrorBoundary>
  );
}

export default App;
