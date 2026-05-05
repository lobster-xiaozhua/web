use flate2::read::GzDecoder;
use flate2::write::GzEncoder;
use flate2::Compression;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::io::Read;
use std::io::Write;

#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

fn compress(data: &[u8]) -> Vec<u8> {
    let mut encoder = GzEncoder::new(Vec::new(), Compression::best());
    encoder.write_all(data).expect("compress write failed");
    encoder.finish().expect("compress finish failed")
}

fn decompress(data: &[u8]) -> Result<Vec<u8>, std::io::Error> {
    let mut decoder = GzDecoder::new(data);
    let mut buf = Vec::new();
    decoder.read_to_end(&mut buf)?;
    Ok(buf)
}

#[pyfunction]
fn compress_py(py: Python<'_>, data: &[u8]) -> PyResult<PyObject> {
    let compressed = py.allow_threads(|| compress(data));
    Ok(PyBytes::new_bound(py, &compressed).into_any().unbind())
}

#[pyfunction]
fn decompress_py(py: Python<'_>, data: &[u8]) -> PyResult<PyObject> {
    let result = py.allow_threads(|| {
        decompress(data).map_err(|e| {
            PyErr::new::<PyValueError, _>(format!("Decompression failed: {}", e))
        })
    })?;
    Ok(PyBytes::new_bound(py, &result).into_any().unbind())
}

#[pymodule]
fn novel_compressor(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compress_py, m)?)?;
    m.add_function(wrap_pyfunction!(decompress_py, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_roundtrip() {
        let original = b"Hello, world! This is a test of the compression module.";
        let compressed = compress(original);
        let decompressed = decompress(&compressed).unwrap();
        assert_eq!(original.as_slice(), decompressed.as_slice());
    }

    #[test]
    fn test_empty_input() {
        let original = b"";
        let compressed = compress(original);
        let decompressed = decompress(&compressed).unwrap();
        assert_eq!(original.as_slice(), decompressed.as_slice());
    }

    #[test]
    fn test_large_text() {
        let original: Vec<u8> = "The quick brown fox jumps over the lazy dog. "
            .repeat(10000)
            .into_bytes();
        let compressed = compress(&original);
        assert!(compressed.len() < original.len());
        let decompressed = decompress(&compressed).unwrap();
        assert_eq!(original, decompressed);
    }

    #[test]
    fn test_binary_data() {
        let original: Vec<u8> = (0u8..=255).collect();
        let compressed = compress(&original);
        let decompressed = decompress(&compressed).unwrap();
        assert_eq!(original, decompressed);
    }

    #[test]
    fn test_decompress_invalid_input() {
        let result = decompress(b"not valid gzip data");
        assert!(result.is_err());
    }
}
