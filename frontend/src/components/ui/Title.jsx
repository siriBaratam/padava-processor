import { Link } from 'react-router-dom';
import OceanBreezeLogo from '../OceanBreezeLogo';
export const Title = () => {
    return (<Link to="/" className="flex items-center space-x-3 group">
              <div className="p-1.5 rounded-xl bg-[#E4EFEE] border border-[#0E6E6A]/30 group-hover:border-[#0E6E6A] group-hover:bg-[#E4EFEE]/90 transition-all duration-200 shadow-sm flex items-center justify-center">
                <OceanBreezeLogo className="w-7 h-7" animated={true} />
              </div>
              <div className="flex flex-col">
                <span className="text-base font-semibold tracking-tight text-[#10201E] group-hover:text-[#0E6E6A] transition-colors leading-tight">
                  EnergyGuard 
                </span>
                <span className="text-[10px] font-mono text-[#4B5A57] tracking-wider uppercase">Supply Chain Resilience</span>
              </div>
            </Link>)
};