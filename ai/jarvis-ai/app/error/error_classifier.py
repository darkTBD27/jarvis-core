from error.error_types import ErrorCategory
from error.error_types import ErrorSeverity
from error.error_types import RetryPolicy


class ErrorClassifier:


    def classify(self, error_message: str):

        message = error_message.lower()


        category = self._detect_category(message)

        severity = self._detect_severity(message)

        retry = self._detect_retry(message)


        return {

            "category": category,

            "severity": severity,

            "retry_policy": retry

        }


    def _detect_category(self, message):

        if "connection refused" in message:

            return ErrorCategory.NETWORK_ERROR


        if "timeout" in message:

            return ErrorCategory.TIMEOUT_ERROR


        if "permission denied" in message:

            return ErrorCategory.PERMISSION_ERROR


        if "not found" in message:

            return ErrorCategory.CONFIG_ERROR


        return ErrorCategory.UNKNOWN


    def _detect_severity(self, message):

        if "fatal" in message:

            return ErrorSeverity.FATAL


        if "critical" in message:

            return ErrorSeverity.CRITICAL


        return ErrorSeverity.ERROR


    def _detect_retry(self, message):

        if "timeout" in message:

            return RetryPolicy.RETRYABLE


        if "connection refused" in message:

            return RetryPolicy.RETRYABLE


        if "permission denied" in message:

            return RetryPolicy.NON_RETRYABLE


        return RetryPolicy.CONDITIONAL
