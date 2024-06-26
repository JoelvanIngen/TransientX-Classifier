from sklearn.cluster import KMeans
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from filetools import list_ext_files, copy_file
from pxreader import PXReader


class Clusters:
    def __init__(self, paths: list[str], filenames: list[str], n_clusters: int):
        self.paths = paths
        self.filenames = filenames
        self.n_clusters = n_clusters

        self.readers = [PXReader(path, filename) for path, filename in zip(paths, filenames)]
        # Unused: r.date_mjd, r.gl, r.gb, r.max_dm, r.dm_diff_from_max, r.distance, r.flux_amp, r.flux_mu, r.flux_sigma
        self.features = [[r.snr, r.width, r.dm]
                         for r in self.readers]

        self.kmeans = KMeans(n_clusters=n_clusters).fit(self.features)
        self.labels = self.kmeans.labels_

    def create_cluster_folder(self):
        for reader, label in zip(self.readers, self.labels):
            copy_file(reader.path, f"clusters/{label+1}", reader.filename)
            copy_file(reader.png_path, f"clusters/{label+1}", reader.png_filename)

    def print_cluster_info(self):
        for reader, label in zip(self.readers, self.labels):
            print(f"PX: {reader.get_info_str()}")
            print(f"Label: {label+1}")
            print("")

    def _plot(self, x, y):
        colours = ['red', 'green', 'blue', 'magenta', 'cyan', 'yellow', 'black']

        # Assure we won't get an index error retrieving colours
        if self.n_clusters > len(colours):
            raise ValueError(f'Plotting does not (yet) support more than {len(colours)} clusters.')

        for i in range(len(self.readers)):
            plt.scatter(x[i], y[i], c=colours[self.labels[i]])

        # Create legend
        patches = [mpatches.Patch(color=colours[i], label=f"Cluster {i + 1}") for i in range(self.n_clusters)]
        plt.legend(handles=patches)

    def plot_cluster_against_time(self):
        x = [reader.date_mjd for reader in self.readers]
        y = [i for i in range(len(self.readers))]

        self._plot(x, y)

        plt.xlabel("Time (MJD)")
        plt.ylabel("Candidate ID")
        plt.show()

    def plot_dm_against_snr(self):
        x = [reader.snr for reader in self.readers]
        y = [reader.dm for reader in self.readers]

        self._plot(x, y)

        plt.xlabel("S/N")
        plt.ylabel("DM")
        plt.show()


def main():
    paths, filenames = list_ext_files('.px', directory='files')

    clusters = Clusters(paths, filenames, n_clusters=4)
    clusters.plot_dm_against_snr()


if __name__ == '__main__':
    main()
