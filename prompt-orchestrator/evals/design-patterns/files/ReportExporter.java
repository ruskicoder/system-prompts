public interface ReportExporter {
    byte[] export(Report report);
}

public class PdfReportExporter implements ReportExporter {
    public byte[] export(Report report) { return PdfRenderer.render(report); }
}

public class ReportExporterFactory {
    public static ReportExporter create() { return new PdfReportExporter(); }
}

public class ReportService {
    private final ReportExporter exporter = ReportExporterFactory.create();
    public byte[] monthly(Report r) { return exporter.export(r); }
}
