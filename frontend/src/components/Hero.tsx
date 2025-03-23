import Link from 'next/link';
import Image from 'next/image';

const Hero = () => {
  return (
    <section className="py-16 md:py-24 px-6 md:px-12 flex flex-col md:flex-row items-center justify-between gap-12">
      <div className="flex-1 space-y-6">
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white leading-tight">
          AI-Powered <span className="text-blue-600 dark:text-blue-400">Legal</span> Assistant
        </h1>
        <p className="text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-2xl">
          Transform your legal workflow with our advanced AI solution. Streamline document review, automate contract analysis, and gain valuable insights with state-of-the-art natural language processing.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 pt-4">
          <Link href="/demo" className="px-6 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 transition-colors text-center font-medium shadow-md hover:shadow-lg">
            Try Free Demo
          </Link>
          <Link href="#features" className="px-6 py-3 rounded-lg bg-gray-100 text-gray-800 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700 transition-colors text-center font-medium shadow-md hover:shadow-lg">
            Learn More
          </Link>
        </div>
        <div className="pt-6 text-sm text-gray-500 dark:text-gray-400 flex items-center gap-4">
          <div className="flex -space-x-2">
            <Image src="https://randomuser.me/api/portraits/women/44.jpg" alt="User" width={32} height={32} className="rounded-full border-2 border-white dark:border-gray-800" />
            <Image src="https://randomuser.me/api/portraits/men/46.jpg" alt="User" width={32} height={32} className="rounded-full border-2 border-white dark:border-gray-800" />
            <Image src="https://randomuser.me/api/portraits/women/45.jpg" alt="User" width={32} height={32} className="rounded-full border-2 border-white dark:border-gray-800" />
          </div>
          <p>Trusted by 1,000+ legal professionals</p>
        </div>
      </div>
      <div className="flex-1 relative h-[400px] w-full md:max-w-[500px]">
        <div className="absolute top-0 -right-4 w-72 h-72 bg-blue-300 dark:bg-blue-900 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-2xl opacity-70 dark:opacity-30 animate-blob"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-purple-300 dark:bg-purple-900 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-2xl opacity-70 dark:opacity-30 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/3 w-72 h-72 bg-pink-300 dark:bg-pink-900 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-2xl opacity-70 dark:opacity-30 animate-blob animation-delay-4000"></div>
        <div className="relative bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 z-10 h-full flex items-center justify-center">
          <Image 
            src="/hero-image.svg" 
            alt="Legal AI Platform" 
            width={400} 
            height={300}
            className="object-contain"
            priority
          />
        </div>
      </div>
    </section>
  );
};

export default Hero; 