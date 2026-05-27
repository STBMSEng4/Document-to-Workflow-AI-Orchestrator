import { readFileSync } from "fs";
import { processPdf } from "@firecrawl/pdf-inspector";

const filePath = process.argv[2];

if (!filePath) {
  console.error(JSON.stringify({ error: "Missing PDF file path" }));
  process.exit(1);
}

try {
  const result = processPdf(readFileSync(filePath));
  process.stdout.write(
    JSON.stringify({
      pdfType: result.pdfType ?? null,
      confidence: result.confidence ?? null,
      markdown: result.markdown ?? "",
      pagesNeedingOcr: result.pagesNeedingOcr ?? [],
    }),
  );
} catch (error) {
  console.error(
    JSON.stringify({
      error: error instanceof Error ? error.message : String(error),
    }),
  );
  process.exit(1);
}
