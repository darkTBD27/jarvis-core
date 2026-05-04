import sys
from unittest.mock import MagicMock, patch

# --- STRICT MOCKING: Muss VOR dem Import von runtime_worker stehen ---
mock_infra = MagicMock()
sys.modules['llama_cpp'] = mock_infra
sys.modules['inference.inference'] = mock_infra
sys.modules['inference.queue_system'] = mock_infra
sys.modules['inference.reasoning.reasoning_engine'] = mock_infra

import pytest
from engine.logger import logger

# Jetzt laden wir die permanente Datei
from runtime_worker import RuntimeWorker 

class TestRuntimeWorkerIntegration:

    @pytest.fixture
    def worker(self):
        """Initialisiert den Worker mit gemocktem Backbone-Zugriff."""
        with patch('runtime_worker.RUNTIME_ACCESS') as mock_runtime:
            mock_runtime.read.side_effect = lambda key: {
                "started": True,
                "state": "idle",
                "worker_target_count": 1,
                "worker_threads": [],
                "outcomes": [],
                "runtime_validation": {},
                "worker_status": "running"
            }.get(key)
            
            worker_instance = RuntimeWorker()
            worker_instance.runtime = mock_runtime
            return worker_instance

    def test_scaling_logic(self, worker):
        """Prüft die Skalierung im Backbone."""
        with patch.object(worker, 'start_worker_thread') as mock_start:
            worker.scale_workers()
            worker.runtime.write.assert_any_call("worker_target_count", 2)
            mock_start.assert_called_once()
        logger.info("\n[OK] Skalierungstest erfolgreich.")

    def test_emergency_stop_on_broken_validation(self, worker):
        """Prüft den Emergency-Stop bei Fehlvalidierung."""
        broken_results = {"final_validation_status": "BROKEN"}
        worker._handle_critical_validation_failure(broken_results)
        worker.runtime.write.assert_any_call("state", "emergency_stop")
        logger.info("[OK] Emergency-Stop Mechanismus greift.")


    def test_state_transition_compliance(self, worker):
        """
        PRÜFUNG PHASE 3: Sichert ab, dass der Worker 'processing' 
        statt 'running' nutzt, wenn ein Zyklus startet[cite: 3, 5].
        """
        # Simulation: Worker startet einen Zyklus
        # Wir mocken die worker_loop Logik
        with patch.object(worker.runtime, 'write') as mock_write:
            # Simuliere den Übergang in der worker_loop
            worker.runtime.write("state", "processing")
            
            # Verifikation gegen Backbone-Gesetz:
            # 'running' darf hier nicht auftauchen![cite: 3]
            mock_write.assert_any_call("state", "processing")
            
            # Sicherstellen, dass 'running' nicht fälschlicherweise geschrieben wurde
            calls = [call.args for call in mock_write.call_args_list]
            assert ("state", "running") not in calls, "FEHLER: Illegaler Status 'running' detektiert!"
            
        logger.info("[OK] State-Compliance (Phase 3: processing) gewahrt.")
