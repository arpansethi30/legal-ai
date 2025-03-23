import Link from 'next/link';
import Image from 'next/image';

const Footer = () => {
  return (
    <footer className="bg-gray-100 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto py-12 px-6 md:px-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 md:gap-12">
          <div className="col-span-1 md:col-span-1">
            <Link href="/" className="flex items-center">
              <span className="text-xl font-bold text-blue-600 dark:text-blue-400">LegalAI</span>
            </Link>
            <p className="mt-4 text-sm text-gray-600 dark:text-gray-300">
              Advanced AI solutions for legal professionals. Streamline your workflow and gain valuable insights.
            </p>
            <div className="mt-6 flex space-x-4">
              <a href="#" className="text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400">
                <span className="sr-only">Twitter</span>
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                </svg>
              </a>
              <a href="#" className="text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400">
                <span className="sr-only">LinkedIn</span>
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                </svg>
              </a>
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider">Product</h3>
            <ul className="mt-4 space-y-3">
              <li>
                <Link href="#features" className="text-base text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
                  Features
                </Link>
              </li>
              <li>
                <Link href="#testimonials" className="text-base text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
                  Testimonials
                </Link>
              </li>
              <li>
                <Link href="#pricing" className="text-base text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="/faqs" className="text-base text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
                  FAQs
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider">Company</h3>
            <ul className="mt-4 space-y-3">
              <li>
                <Link href="/about" className="text-base text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
                  About
                </Link>
              </li>
              <li>
                <Link href="/blog" className="text-base text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
                  Blog
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-base text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
                  Contact
                </Link>
              </li>
              <li>
                <Link href="/careers" className="text-base text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
                  Careers
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider">Legal</h3>
            <ul className="mt-4 space-y-3">
              <li>
                <Link href="/privacy" className="text-base text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-base text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/security" className="text-base text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
                  Security
                </Link>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            &copy; {new Date().getFullYear()} LegalAI. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 