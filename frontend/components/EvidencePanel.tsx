import type { RagChunk } from "@/lib/types";
import { evidenceLabels } from "@/lib/labels";

interface EvidencePanelProps {
  chunks: RagChunk[];
  citation: string | null;
  contractClauses?: string | null;
}

function normalise(s: string): string {
  return s.replace(/\s+/g, " ").trim();
}

/**
 * Find the citation inside `chunkText` using case-insensitive, whitespace-normalised comparison.
 * Returns the start/end indices inside the ORIGINAL `chunkText` string, or null if not found.
 */
function findSpanInChunk(
  chunkText: string,
  citation: string,
): { start: number; end: number } | null {
  const normChunk = normalise(chunkText);
  const normCitation = normalise(citation);

  if (!normCitation) return null;

  const normIdx = normChunk.toLowerCase().indexOf(normCitation.toLowerCase());
  if (normIdx === -1) return null;

  let origPos = 0;
  let normPos = 0;
  let startOrig = -1;
  let endOrig = -1;

  while (origPos < chunkText.length && normPos <= normChunk.length) {
    if (normPos === normIdx) startOrig = origPos;
    if (startOrig !== -1 && normPos === normIdx + normCitation.length) {
      endOrig = origPos;
      break;
    }
    if (/\s/.test(chunkText[origPos])) {
      while (origPos < chunkText.length && /\s/.test(chunkText[origPos]))
        origPos++;
      if (normPos < normChunk.length && normChunk[normPos] === " ") normPos++;
    } else {
      origPos++;
      normPos++;
    }
  }

  if (startOrig !== -1 && endOrig === -1) {
    endOrig = origPos;
  }

  if (startOrig === -1 || endOrig === -1 || startOrig >= endOrig) return null;
  return { start: startOrig, end: endOrig };
}

function renderHighlighted(
  chunkText: string,
  citation: string | null,
): { node: React.ReactNode; matched: boolean } {
  if (!citation) return { node: chunkText, matched: false };

  const span = findSpanInChunk(chunkText, citation);
  if (!span) return { node: chunkText, matched: false };

  return {
    matched: true,
    node: (
      <>
        {chunkText.slice(0, span.start)}
        <mark className="evidence-highlight">
          {chunkText.slice(span.start, span.end)}
        </mark>
        {chunkText.slice(span.end)}
      </>
    ),
  };
}

function SectionHeading({ label }: { label: string }) {
  return (
    <p className="font-mono text-xs text-muted-foreground uppercase tracking-widest mb-2">
      {label}
    </p>
  );
}

export function EvidencePanel({
  chunks,
  citation,
  contractClauses,
}: EvidencePanelProps) {
  const hasChunks = Array.isArray(chunks) && chunks.length > 0;
  const hasClauses =
    typeof contractClauses === "string" && contractClauses.trim().length > 0;
  let citationMatchedInChunks = false;
  let citationMatchedInClauses = false;

  if (citation) {
    if (hasChunks) {
      for (const chunk of chunks) {
        if (findSpanInChunk(chunk.text, citation)) {
          citationMatchedInChunks = true;
          break;
        }
      }
    }
    if (!citationMatchedInChunks && hasClauses) {
      if (findSpanInChunk(contractClauses as string, citation)) {
        citationMatchedInClauses = true;
      }
    }
  }

  const citationMatched = citationMatchedInChunks || citationMatchedInClauses;

  return (
    <div className="flex flex-col gap-6">
      {/* ── Section 1: RAG chunks ── */}
      <div>
        <SectionHeading label={evidenceLabels.ragChunksHeading} />
        {hasChunks ? (
          <div className="flex flex-col gap-4">
            {chunks.map((chunk, i) => {
              const { node } = renderHighlighted(chunk.text, citation);
              return (
                <div
                  key={i}
                  className="bg-evidence-surface rounded-md border border-border overflow-hidden"
                >
                  {/* Chunk header */}
                  <div className="flex items-center justify-between px-4 py-2 border-b border-border">
                    <span className="font-mono text-xs text-primary truncate">
                      {chunk.source_section}
                    </span>
                    <div className="flex items-center gap-3 shrink-0 ml-4">
                      <span className="font-mono text-xs text-muted-foreground">
                        Pág. {chunk.page}
                      </span>
                      <span className="font-mono text-xs text-muted-foreground">
                        Puntaje{" "}
                        <span className="text-foreground">
                          {chunk.score.toFixed(3)}
                        </span>
                      </span>
                    </div>
                  </div>
                  {/* Chunk body with optional highlight */}
                  <p className="px-4 py-3 text-sm leading-relaxed text-foreground/90">
                    {node}
                  </p>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground italic">
            {evidenceLabels.noRagChunks}
          </p>
        )}
      </div>

      {/* ── Section 2: Contract clauses ── */}
      <div>
        <SectionHeading label={evidenceLabels.contractClausesHeading} />
        {hasClauses ? (
          <div className="bg-evidence-surface rounded-md border border-border overflow-hidden">
            <p className="px-4 py-3 text-sm leading-relaxed font-mono text-foreground/90 whitespace-pre-wrap">
              {citationMatchedInClauses
                ? renderHighlighted(contractClauses as string, citation).node
                : contractClauses}
            </p>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground italic">
            {evidenceLabels.noContractClauses}
          </p>
        )}
      </div>

      {citation && !citationMatched && (
        <div className="rounded-md border border-amber-500/40 bg-amber-500/5 overflow-hidden">
          <div className="px-4 py-2 border-b border-amber-500/30">
            <span className="font-mono text-xs text-amber-600 dark:text-amber-400 uppercase tracking-wider">
              {evidenceLabels.citationNotFound}
            </span>
          </div>
          <p className="px-4 py-3 text-sm leading-relaxed font-mono text-foreground/80">
            <mark className="evidence-highlight">&ldquo;{citation}&rdquo;</mark>
          </p>
          <p className="px-4 pb-3 text-xs text-muted-foreground italic">
            {evidenceLabels.citationNotFoundDetail}
          </p>
        </div>
      )}
    </div>
  );
}
