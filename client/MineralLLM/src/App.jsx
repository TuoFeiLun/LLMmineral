import { useState } from 'react';
import { AppShell } from '@mantine/core';
import { Navbar } from './components/Navbar/Navbar';
import { ChatInterface } from './components/Chat/ChatInterface';
import { CollectionManager } from './components/Collections/CollectionManager';
import { FileUpload } from './components/FileUpload/FileUpload';
import { AnswerEvaluation } from './components/AnswerEvaluation/AnswerEvaluation';

function App() {
  const [activeView, setActiveView] = useState('chat');

  const renderContent = () => {
    switch (activeView) {
      case 'chat':
        return <ChatInterface />;
      case 'collections':
        return <CollectionManager />;
      case 'upload':
        return <FileUpload />;
      case 'evaluation':
        return <AnswerEvaluation />;
      default:
        return <ChatInterface />;
    }
  };

  return (
    <AppShell
      navbar={{
        width: 80,
        breakpoint: 'sm',
      }}
      padding="md"
    >
      <AppShell.Navbar>
        <Navbar activeView={activeView} setActiveView={setActiveView} />
      </AppShell.Navbar>

      <AppShell.Main>
        {renderContent()}
      </AppShell.Main>
    </AppShell>
  );
}

export default App;