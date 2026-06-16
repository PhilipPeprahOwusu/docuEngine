'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  User,
  Calendar,
  AlertTriangle,
} from 'lucide-react';
import { approvalsAPI } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';

interface Exception {
  exception_id: string;
  document_id: string;
  policy_id: string;
  status: string;
  exception_reason: string;
  requested_by: string;
  requester_name: string;
  approved_by?: string;
  approver_name?: string;
  approval_timestamp?: string;
  rejection_reason?: string;
  created_at: string;
}

export default function ApprovalsPage() {
  const [activeTab, setActiveTab] = useState('pending');
  const [pendingExceptions, setPendingExceptions] = useState<Exception[]>([]);
  const [approvedExceptions, setApprovedExceptions] = useState<Exception[]>([]);
  const [rejectedExceptions, setRejectedExceptions] = useState<Exception[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);

  const user = useAuthStore((state) => state.user);
  const isApprover = user?.role === 'approver' || user?.role === 'admin';

  useEffect(() => {
    loadExceptions();
  }, []);

  const loadExceptions = async () => {
    setLoading(true);
    try {
      const [pending, approved, rejected] = await Promise.all([
        approvalsAPI.getPendingExceptions(),
        approvalsAPI.getApprovedExceptions(),
        approvalsAPI.getRejectedExceptions(),
      ]);

      setPendingExceptions(pending.data);
      setApprovedExceptions(approved.data);
      setRejectedExceptions(rejected.data);
    } catch (error) {
      console.error('Failed to load exceptions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (exceptionId: string) => {
    setProcessingId(exceptionId);
    try {
      await approvalsAPI.approveException(exceptionId);
      await loadExceptions(); // Reload data
      alert('Exception approved successfully');
    } catch (error: any) {
      console.error('Failed to approve exception:', error);
      alert(error.response?.data?.detail || 'Failed to approve exception');
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (exceptionId: string) => {
    const reason = prompt('Enter rejection reason (optional):');
    setProcessingId(exceptionId);
    try {
      await approvalsAPI.rejectException(exceptionId, reason || undefined);
      await loadExceptions(); // Reload data
      alert('Exception rejected');
    } catch (error: any) {
      console.error('Failed to reject exception:', error);
      alert(error.response?.data?.detail || 'Failed to reject exception');
    } finally {
      setProcessingId(null);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const ExceptionCard = ({ exception }: { exception: Exception }) => {
    const isProcessing = processingId === exception.exception_id;

    return (
      <Card className="mb-4">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-lg flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Policy Exception Request
              </CardTitle>
              <CardDescription className="mt-2">
                <div className="flex items-center gap-2 text-sm">
                  <User className="h-4 w-4" />
                  Requested by: <span className="font-medium">{exception.requester_name}</span>
                </div>
                <div className="flex items-center gap-2 text-sm mt-1">
                  <Calendar className="h-4 w-4" />
                  {formatDate(exception.created_at)}
                </div>
              </CardDescription>
            </div>
            <Badge
              variant={
                exception.status === 'approved'
                  ? 'default'
                  : exception.status === 'rejected'
                  ? 'destructive'
                  : 'secondary'
              }
            >
              {exception.status.toUpperCase()}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Exception Reason */}
            <div>
              <h4 className="font-semibold text-sm mb-2 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                Exception Reason
              </h4>
              <p className="text-sm text-muted-foreground bg-slate-50 p-3 rounded">
                {exception.exception_reason}
              </p>
            </div>

            {/* Approval/Rejection Info */}
            {exception.status === 'approved' && exception.approver_name && (
              <div className="bg-green-50 p-3 rounded">
                <p className="text-sm">
                  <span className="font-semibold text-green-800">Approved by:</span>{' '}
                  {exception.approver_name}
                </p>
                {exception.approval_timestamp && (
                  <p className="text-sm text-green-700">
                    on {formatDate(exception.approval_timestamp)}
                  </p>
                )}
              </div>
            )}

            {exception.status === 'rejected' && (
              <div className="bg-red-50 p-3 rounded">
                <p className="text-sm">
                  <span className="font-semibold text-red-800">Rejected by:</span>{' '}
                  {exception.approver_name || 'Unknown'}
                </p>
                {exception.rejection_reason && (
                  <p className="text-sm text-red-700 mt-2">
                    <span className="font-semibold">Reason:</span> {exception.rejection_reason}
                  </p>
                )}
              </div>
            )}

            {/* Action Buttons (Approver-only, Pending only) */}
            {isApprover && exception.status === 'pending' && (
              <div className="flex gap-2 pt-2">
                <Button
                  onClick={() => handleApprove(exception.exception_id)}
                  disabled={isProcessing}
                  className="flex-1"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  {isProcessing ? 'Approving...' : 'Approve'}
                </Button>
                <Button
                  onClick={() => handleReject(exception.exception_id)}
                  disabled={isProcessing}
                  variant="destructive"
                  className="flex-1"
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  {isProcessing ? 'Rejecting...' : 'Reject'}
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading approvals...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">
          {isApprover ? 'Approvals' : 'My Exception Requests'}
        </h1>
        <p className="text-muted-foreground">
          {isApprover
            ? 'Review and approve policy exception requests from your team'
            : 'Track the status of your policy exception requests'}
        </p>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="pending" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Pending ({pendingExceptions.length})
          </TabsTrigger>
          <TabsTrigger value="approved" className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4" />
            Approved ({approvedExceptions.length})
          </TabsTrigger>
          <TabsTrigger value="rejected" className="flex items-center gap-2">
            <XCircle className="h-4 w-4" />
            Rejected ({rejectedExceptions.length})
          </TabsTrigger>
        </TabsList>

        {/* Pending Tab */}
        <TabsContent value="pending" className="mt-6">
          {pendingExceptions.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">No pending exceptions</p>
              </CardContent>
            </Card>
          ) : (
            <div>
              {pendingExceptions.map((exception) => (
                <ExceptionCard key={exception.exception_id} exception={exception} />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Approved Tab */}
        <TabsContent value="approved" className="mt-6">
          {approvedExceptions.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <CheckCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">No approved exceptions</p>
              </CardContent>
            </Card>
          ) : (
            <div>
              {approvedExceptions.map((exception) => (
                <ExceptionCard key={exception.exception_id} exception={exception} />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Rejected Tab */}
        <TabsContent value="rejected" className="mt-6">
          {rejectedExceptions.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <XCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">No rejected exceptions</p>
              </CardContent>
            </Card>
          ) : (
            <div>
              {rejectedExceptions.map((exception) => (
                <ExceptionCard key={exception.exception_id} exception={exception} />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
