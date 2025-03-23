import Link from 'next/link';

const Navbar = () => {
  return (
    <nav className="w-full py-4 px-6 md:px-12 flex justify-between items-center bg-white/90 backdrop-blur-md dark:bg-black/90 sticky top-0 z-50 border-b border-gray-200 dark:border-gray-800">
      <div className="flex items-center">
        <Link href="/" className="text-xl font-bold text-blue-600 dark:text-blue-400">
          LegalAI
        </Link>
      </div>
      
      <div className="hidden md:flex items-center space-x-8">
        <Link href="#features" className="text-gray-700 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400 transition-colors">
          Features
        </Link>
        <Link href="#benefits" className="text-gray-700 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400 transition-colors">
          Benefits
        </Link>
        <Link href="#testimonials" className="text-gray-700 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400 transition-colors">
          Testimonials
        </Link>
        <Link href="#pricing" className="text-gray-700 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400 transition-colors">
          Pricing
        </Link>
      </div>
      
      <div className="flex items-center space-x-4">
        <Link href="/login" className="px-4 py-2 rounded-md bg-transparent border border-blue-600 text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:border-blue-400 dark:hover:bg-blue-900/20 transition-colors">
          Log in
        </Link>
        <Link href="/signup" className="px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 transition-colors">
          Sign up
        </Link>
      </div>
    </nav>
  );
};

export default Navbar; 