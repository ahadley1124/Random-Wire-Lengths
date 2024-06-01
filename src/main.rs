use std::env;
use std::process;

const HAM_BANDS_MHZ: [(u32, u32); 11] = [
	(160, 2000),
	(80, 4000),
	(60, 5335),
	(40, 7000),
	(30, 10150),
	(20, 14000),
	(17, 18068),
	(15, 21000),
	(12, 24890),
	(10, 28000),
	(6, 50000),
];

fn cli(args: Vec<String>) -> (Vec<u32>, bool, bool) {
	let mut bands: Vec<u32> = Vec::new();
	let mut fullwave = false;
	let mut metric = false;

	let mut iter = args.iter().skip(1);
	while let Some(arg) = iter.next() {
		match arg.as_str() {
			"-f" => fullwave = true,
			"-m" => metric = true,
			_ => {
				if let Ok(band) = arg.parse::<u32>() {
					bands.push(band);
				} else {
					usage(&args[0]);
				}
			}
		}
	}

	bands.sort_unstable_by(|a, b| b.cmp(a));

	if bands.is_empty() {
		usage(&args[0]);
	}

	(bands, metric, fullwave)
}

fn edges_mhz(bands: &[u32]) -> Vec<(u32, u32)> {
	let mut edges: Vec<(u32, u32)> = Vec::new();

	for band in bands {
		if let Some(band_mhz) = HAM_BANDS_MHZ.iter().find(|(b, _)| *b == *band) {
			edges.push(*band_mhz);
		} else {
			usage("endfed");
		}
	}

	edges
}

fn graph(title: &str, edges_ft: &[(f64, f64)], metric: bool, len_qtr_ft: f64) {
	let mut x_max: f32 = 0.0;

	let mut fig = plt::figure::Figure::new();
	fig.set_size_inches(8.0, 1.25);
	fig.set_dpi(120.0);

	let ax = fig.add_subplot(1, 1, 1, None);
	ax.set_title(title, &[]);
	ax.set_xlabel(format!("Wire Length ({})", if metric { "m" } else { "ft" }));
	ax.set_yticks(&[]);
	ax.set_ylim(0.0, 1.0);
	ax.grid(true);

	let len_qtr_ft = if metric {
		len_qtr_ft * 12.0 / 39.37
	} else {
		len_qtr_ft
	};

	for edge in edges_ft {
		let (e0, e1) = if metric {
			(edge.0 * 12.0 / 39.37, edge.1 * 12.0 / 39.37)
		} else {
			(edge.0, edge.1)
		};

		ax.fill([e0, e0, e1, e1], [0.0, 1.0, 1.0, 0.0], Some("r"), None);
		x_max = x_max.max(e1);
	}

	ax.set_xlim(len_qtr_ft, x_max);
	fig.tight_layout();
	fig.show().unwrap();
}

fn high_v(band_mhz: (u32, u32), len_max_ft: f64) -> Vec<(f64, f64)> {
	let (len1_ft, len0_ft) = (468.0 / band_mhz.0 as f64, 468.0 / band_mhz.1 as f64);
	let multiples = (len_max_ft / len0_ft) as usize;
	let mut res_ft = vec![(0.0, 0.0); multiples];

	for (i, res) in res_ft.iter_mut().enumerate() {
		let n = i as f64 + 1.0;
		res.0 = n * len0_ft;
		res.1 = n * len1_ft;
	}

	res_ft
}

fn usage(prog: &str) {
	println!("Usage: {} [-f] [-m] band...", prog);
	println!("  -f, graph fullwave (halfwave default).");
	println!("  -m, metric lengths.");
	println!("  band, integer in 160,80,60,40,30,20,17,15,12,10,6 m");
	println!("  E.g., {} 40 20 15 10", prog);
	process::exit(1);
}

fn main() {
	let args: Vec<String> = env::args().collect();
	let (bands, metric, fullwave) = cli(args);

	let edges_mhz = edges_mhz(&bands);

	let len_qtr_ft = 234.0 / edges_mhz[0].0 as f64;
	let len_max_ft = if fullwave {
		2.0 * 468.0 / edges_mhz[0].0 as f64
	} else {
		468.0 / edges_mhz[0].0 as f64
	};

	let mut all_ft = vec![(0.0, len_qtr_ft)];
	for band_mhz in edges_mhz {
		let res_ft = high_v(band_mhz, len_max_ft);
		all_ft.extend(res_ft);
	}

	let s = bands
		.iter()
		.map(|b| b.to_string())
		.collect::<Vec<String>>()
		.join(", ");
	graph(&format!("High Voltage Lengths for {} m", s), &all_ft, metric, len_qtr_ft);
}
