import { ProcessWorkspace } from '../ProcessWorkspace';
import { leaveSystemConfig } from '../configs';

export default function LeaveWorkspacePage() {
  return <ProcessWorkspace kind="leave" config={leaveSystemConfig} recordsLabel="Заявки" />;
}
