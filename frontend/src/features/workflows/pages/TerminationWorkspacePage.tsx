import { ProcessWorkspace } from '../ProcessWorkspace';
import { terminationSystemConfig } from '../configs';

export default function TerminationWorkspacePage() {
  return <ProcessWorkspace kind="termination" config={terminationSystemConfig} recordsLabel="Дела" />;
}
