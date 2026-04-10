import { OperatorConsole } from "@/components/operator-console";
import { fetchConsoleState, fetchRecords } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function Home() {
  const [consoleState, records] = await Promise.all([
    fetchConsoleState(),
    fetchRecords({ limit: 500 }),
  ]);

  return <OperatorConsole initialConsoleState={consoleState} initialRecords={records} />;
}
