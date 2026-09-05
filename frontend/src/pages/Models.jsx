import { Boxes, ChevronRight, Database, Maximize2 } from 'lucide-react';
import { api } from '../api/client';
import { useApi } from '../hooks/useApi';
import Panel from '../components/ui/Panel';
import Badge from '../components/ui/Badge';

function formatCapabilityKey(key) {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function getCapabilities(capabilities) {
  if (!capabilities || typeof capabilities !== 'object') {
    return [];
  }

  return Object.entries(capabilities)
    .filter(([, value]) => value === true)
    .map(([key]) => formatCapabilityKey(key));
}

export default function Models() {
  const q = useApi(api.models, []);

  const models = Array.isArray(q.data) ? q.data : [];

  return (
    <div>
      <div className="page-heading">
        <div>
          <div className="eyebrow">MODEL REGISTRY</div>
          <h1>Models</h1>
          <p>Available model definitions and routing capabilities.</p>
        </div>
      </div>

      <Panel
        title="Registered models"
        subtitle="Read from the live model registry"
      >
        {q.loading && (
          <div className="empty">
            Loading models...
          </div>
        )}

        {q.error && (
          <div className="empty">
            <strong>Unable to load models</strong>
            <br />
            <small>
              {q.error.response?.data?.detail ||
                q.error.message ||
                'The backend returned an error.'}
            </small>
          </div>
        )}

        {!q.loading && !q.error && models.length === 0 && (
          <div className="empty">
            <Database size={20} />
            <span>No models are registered in the backend.</span>
          </div>
        )}

        {!q.loading && !q.error && models.length > 0 && (
          <div className="model-grid">
            {models.map((model) => {
              const capabilities = getCapabilities(model.capabilities);

              return (
                <div className="model-card" key={model.id}>
                  <div className="model-icon">
                    <Boxes size={18} />
                  </div>

                  <div className="model-main">
                    <div className="model-title">
                      <div>
                        <b>{model.name}</b>
                        <Badge>
                          {capabilities.length} capabilities
                        </Badge>
                      </div>
                    </div>

                    <small className="mono">
                      {model.id}
                    </small>

                    <div className="model-meta">
                      <span>
                        Context: {model.context_window?.toLocaleString() ?? '—'}
                      </span>
                    </div>

                    {capabilities.length > 0 && (
                      <div className="chips">
                        {capabilities.slice(0, 6).map((capability) => (
                          <span key={capability}>
                            {capability}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <ChevronRight size={17} />
                </div>
              );
            })}
          </div>
        )}
      </Panel>
    </div>
  );
}