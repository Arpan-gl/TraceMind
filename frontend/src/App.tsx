import React from "react";
import { AppProvider, useAppContext } from "./state/app-context";
import { AppLayout } from "./components/AppLayout";
import Intro from "./pages/Intro";

function Content() {
  const { token } = useAppContext();
  if (!token) {
    return <Intro />;
  }
  return <AppLayout />;
}

export default function App() {
  return (
    <AppProvider>
      <Content />
    </AppProvider>
  );
}
