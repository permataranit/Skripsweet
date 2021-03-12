-- phpMyAdmin SQL Dump
-- version 4.6.5.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 22, 2019 at 11:01 PM
-- Server version: 10.1.21-MariaDB
-- PHP Version: 5.6.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `rfesvm`
--

-- --------------------------------------------------------

--
-- Table structure for table `dataset`
--

CREATE TABLE `dataset` (
  `id_data` int(100) NOT NULL,
  `nama` varchar(1000) NOT NULL,
  `header` varchar(750) NOT NULL,
  `label1` varchar(750) NOT NULL,
  `label2` varchar(750) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `dataset`
--

INSERT INTO `dataset` (`id_data`, `nama`, `header`, `label1`, `label2`) VALUES
(1, 'data_17_rna', 'label', 'normal', 'breast'),
(5, 'data_1881_200', 'label', 'normal', 'breast'),
(13, 'data_315_200', 'label', 'normal', 'breast'),
(21, 'hapus', 'label', 'normal', 'breast'),
(22, 'coba3', 'label', 'normal', 'breast');

-- --------------------------------------------------------

--
-- Table structure for table `riwayat_hasil`
--

CREATE TABLE `riwayat_hasil` (
  `id_hasil` int(11) NOT NULL,
  `id_data` int(11) NOT NULL,
  `nama_dtset` varchar(1000) NOT NULL,
  `lrate` double NOT NULL,
  `lammada` double NOT NULL,
  `ce` double NOT NULL,
  `epsi` double NOT NULL,
  `maxepoh` int(11) NOT NULL,
  `kafold` int(11) NOT NULL,
  `akurasi` double NOT NULL,
  `sensi` double NOT NULL,
  `spesi` double NOT NULL,
  `evaluasi` varchar(1000) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `riwayat_hasil`
--

INSERT INTO `riwayat_hasil` (`id_hasil`, `id_data`, `nama_dtset`, `lrate`, `lammada`, `ce`, `epsi`, `maxepoh`, `kafold`, `akurasi`, `sensi`, `spesi`, `evaluasi`) VALUES
(8, 13, 'data_315_200', 0.0005, 0.05, 0.0005, 0.000001, 500, 10, 98.5, 100, 97, 'sudah'),
(9, 5, 'data_1881_200', 0.0005, 0.05, 0.0005, 0.000001, 500, 10, 92.5, 100, 85, 'sudah'),
(16, 22, 'coba3', 0.5, 0.05, 0.005, 0.00001, 50, 5, 92, 85, 99, 'belum');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `dataset`
--
ALTER TABLE `dataset`
  ADD PRIMARY KEY (`id_data`);

--
-- Indexes for table `riwayat_hasil`
--
ALTER TABLE `riwayat_hasil`
  ADD PRIMARY KEY (`id_hasil`),
  ADD KEY `id_data` (`id_data`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `dataset`
--
ALTER TABLE `dataset`
  MODIFY `id_data` int(100) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;
--
-- AUTO_INCREMENT for table `riwayat_hasil`
--
ALTER TABLE `riwayat_hasil`
  MODIFY `id_hasil` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `riwayat_hasil`
--
ALTER TABLE `riwayat_hasil`
  ADD CONSTRAINT `fk_hasil_dataset` FOREIGN KEY (`id_data`) REFERENCES `dataset` (`id_data`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
